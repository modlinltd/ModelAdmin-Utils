from collections import defaultdict, Iterable
import logging
import operator

from django.contrib.admin.util import lookup_needs_distinct
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


class GenericSearchMixin(object):
    """
    Overrides the ModelAdmin.get_search_results method to allow searching
    through a generic relation fields.

    For quick set up, simply use a GenericForeignKey field name as the prefix
    in 'search_fields'.

    E.g: for a field named 'related_to' you can use the following:
    search_fields = ('related_to__fname', 'related_to__email', ...)

    Optionally, you may define 'related_search_mapping' in the ModelAdmin
    to explicitely define a generic field's object id and content types
    (this is useful to limit the content types).

    Notes:
    * Required Django > 1.6
    * Currently assumes id of related objects are unique across all models
    """
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('search.GenericSearchMixin')
        return super(GenericSearchMixin, self).__init__(*args, **kwargs)

    def get_search_results(self, request, queryset, search_term):
        def generate_q_object(orm_lookups):
            """
            Generate Or'ed queries from orm_lookups (fields)
            and every bit of the search_term (query).
            """
            q = Q()
            for bit in search_term.split():
                or_queries = [Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                if or_queries:
                    q = (q & reduce(operator.or_, or_queries))
            return q

        # Apply keyword searches.
        def construct_search(field_name):
            """
            Parse field_name to allow advanced searches using the
            prefixes: '^', '=', '@' and no prefix (default)
            """
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        def parse_related_fields():
            """
            Go over the search_fields to look for fields that exist in the
            related_search_mapping
            """
            normal_fields = []
            generic_search_fields = defaultdict(list)
            for field in self.search_fields:
                for rfield in self.related_search_mapping:
                    if field.startswith(rfield):
                        inner_field = field[len(rfield) + 2:]
                        generic_search_fields[rfield].append(
                            # get the field name after 'rfield__'
                            construct_search(inner_field)
                        )
                    else:
                        normal_fields.append(field)
            return normal_fields, generic_search_fields

        def get_generic_field(model, field_name):
            """
            Find the given generic_field name in the given model and verify
            it is a GenericForeignKey, otherwise raise an Exeption.
            """
            for f in model._meta.virtual_fields:
                if f.name == field_name:
                    if not isinstance(f, GenericForeignKey):
                        raise Exception(
                            'Given field %s is not an instance of '
                            'GenericForeignKey' % field_name)
                    return f

        def get_object_id(model, generic_field):
            """
            Return the foreign key field for a given GenericForeignKey
            in a given model
            """
            self.logger.debug('related_search_mapping did not define object_id, '
                         'attempting to find using GenericForeignKey %s in '
                         'model %s', generic_field, model)
            field = get_generic_field(model, generic_field)
            if field:
                return field.fk_field
            raise Exception('Given field %s does not exist in registered model'
                            ' %s and no object_id provided' % (
                                generic_field, model))

        def get_content_types(model, generic_field):
            """
            Return the content types allowed for a given GenericForeignKey
            in a given model
            """
            self.logger.debug('related_search_mapping did not define ctypes, '
                         'attempting to find using GenericForeignKey %s in '
                         'model %s', generic_field, model)
            field = get_generic_field(model, generic_field)
            if field:
                return field.ct_field
            raise Exception('Given field %s does not exist in registered model'
                            ' %s and no object_id provided' % (
                                generic_field, model))

        def get_related_ids(fields_mapping):
            """
            Takes a dict of {generic_field_name: list_of_inner_Fields}, performs
            the query on the related object models (using defined or calculated
            content types) and returns the ids of the result objects.
            """
            def get_ctype_models(ctypes):
                """
                Gets model classes from the passed argument, which can be:

                a. a dict which can be extrapolated into a query filter.
                b. a Q object which can be passed to a query filter.
                c. an iterable of 2 element tuples as (app_label, model)
                """
                if isinstance(ctypes, dict):
                    if not ctypes:
                        self.logger.warn("""
This is a very inefficient query! Each search argument is going to query
all model classes. Please limit ContentType choices the FK if possible,
or define a 'related_search_mapping' argument which limits the ctypes.""")
                    return [ct.model_class()
                            for ct in ContentType.objects.filter(**ctypes)]
                elif isinstance(ctypes, Q):
                    return [ct.model_class()
                            for ct in ContentType.objects.filter(ctypes)]
                elif isinstance(ctypes, Iterable):
                    return [ContentType.objects.get(
                            app_label=app, model=model).model_class()
                            for app, model in ctypes]
                raise Exception("Invalid argument passed, must be one of: "
                                "<dict>, <Q>, <iterable of 2 elem. tuples>")

            ids = defaultdict(list)
            for rel_field, fields in fields_mapping.items():
                query = generate_q_object(fields)
                if not query:
                    self.logger.warn('No Q instance returned')
                    continue

                obj_id = (self.related_search_mapping[rel_field].get('object_id') or
                          get_object_id(self.model, rel_field))
                ctypes = (self.related_search_mapping[rel_field].get('ctypes') or
                          get_content_types(self.model, rel_field))
                models = get_ctype_models(ctypes)
                for model in models:
                    ids[obj_id].extend(
                        model.objects.filter(query).values_list(
                            'pk', flat=True)
                    )
            return ids

        use_distinct = False
        if not search_term:
            return queryset, use_distinct

        non_generic_fields, generic_fields = parse_related_fields()
        related_ids = get_related_ids(generic_fields)

        # initial orm lookups (for normal fields)
        orm_lookups = [construct_search(str(search_field))
                       for search_field in non_generic_fields]
        for bit in search_term.split():
            or_queries = [Q(**{orm_lookup: bit})
                          for orm_lookup in orm_lookups]

            # append generic related filters to or_queries
            for obj_id, ids_list in related_ids.items():
                or_queries.append(Q(
                    **{
                        '%s__in' % obj_id: ids_list
                    }
                ))
            query = reduce(operator.or_, or_queries)
            queryset = queryset.filter(query)
        if not use_distinct:
            for search_spec in orm_lookups:
                if lookup_needs_distinct(self.opts, search_spec):
                    use_distinct = True
                    break
        return queryset, use_distinct
