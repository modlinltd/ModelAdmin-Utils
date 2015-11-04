import logging

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import get_model

from ..mixins import LimitedInlineFormset

logger = logging.getLogger('modeladmin_utils.templatetags.links')

register = template.Library()


@register.assignment_tag
def link_to_changelist(inline_formset, original, *args, **kwargs):
    """
    Returns a changelist url of the inline_formset model, using
    the original (a related object) instance as a filter.

    Requires either setting an explicit "unlimited model" in the inline
    or a valid related field to the child model (inline_formset.opts.model),
    as well as a registered ModelAdmin for that related module
    (otherwise an Exception is raised)
    """
    if not inline_formset.formset.__class__ in LimitedInlineFormset.__subclasses__():
        return

    if getattr(inline_formset.opts, 'unlimited_changelist_model', None):
        model_path = inline_formset.opts.unlimited_changelist_model
        model = get_model(*model_path.split('.'))
    elif inline_formset.model_admin:
        model = inline_formset.opts.model
    else:
        logger.warn('No model found for the unlimited changelist')
        return ''

    app_label = model._meta.app_label
    model_name = getattr(model._meta, 'model_name', model._meta.module_name)
    parent_model = inline_formset.model_admin.model
    field_name = None
    for field in model._meta.fields:
        if not hasattr(field, "related"):
            continue
        if field.related.parent_model == parent_model:
            field_name = field.name

    if not field_name:
        raise Exception("No related model found or no ModelAdmin registered")

    return "{base}?{query}".format(
        base=reverse("admin:%s_%s_changelist" % (app_label, model_name)),
        query=("%s=%s" % (field_name, original.pk))
    )


@register.filter
def content_type(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj)
