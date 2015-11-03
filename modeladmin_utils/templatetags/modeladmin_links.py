from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from ..mixins import LimitedInlineFormset

register = template.Library()


@register.assignment_tag
def link_to_changelist(inline_formset, original, *args, **kwargs):
    """
    Returns a changelist url of the inline_formset model, using
    the original (a related object) instance as a filter.

    Requires a valid related field on the child (inline_formset.opts.model),
    and a registered ModelAdmin for that child module (otherwise a
    `NoReverseMatch` exception is raised)
    """
    if not inline_formset.formset.__class__ in LimitedInlineFormset.__subclasses__():
        return

    if inline_formset.model_admin:
        app_label = inline_formset.opts.model._meta.app_label
        model_name = inline_formset.opts.model._meta.model_name
        inline_model = inline_formset.opts.model
        parent_model = inline_formset.model_admin.model
        field_name = None
        for field in inline_model._meta.fields:
            if not hasattr(field, "related"):
                continue
            if field.related.parent_model == parent_model:
                field_name = field.name
        if not field_name:
            raise Exception("Bad changelist relation")
        return "{base}?{query}".format(
            base=reverse("admin:%s_%s_changelist" % (app_label, model_name)),
            query=("%s=%s" % (field_name, original.pk))
        )


@register.filter
def content_type(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj)
