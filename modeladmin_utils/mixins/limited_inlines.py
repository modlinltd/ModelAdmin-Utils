from django.conf import settings
from django.forms.models import BaseInlineFormSet


class LimitedInlineFormset(BaseInlineFormSet):
    """
    A specialized subclass of BaseInlineFormSet which limits the queryset
    to a maximum (specified in settings: default to 15).
    """
    limiting_inlines = True

    def get_queryset(self):
        if not hasattr(self, "_queryset"):
            qs = super(LimitedInlineFormset, self).get_queryset()
            limit = getattr(settings, "INLINES_MAX_LIMIT", 15)
            self.total_count = qs.count()
            self._queryset = qs[:limit]
            self.limited_count = self._queryset.count()
        return self._queryset


class LimitInlinesAdminMixin(object):
    """
    Set ModelAdmin.limit_inlines to a tuple of InlineModelAdmin
    classes you wish to be limited.

    Overrides the inline formset with `LimitedInlineFormset`.
    """
    def get_formsets(self, request, obj=None):
        limit_inlines = getattr(self, "limit_inlines", [])
        for inline in self.get_inline_instances(request, obj):
            kwargs = {}
            if inline.__class__ in limit_inlines:
                kwargs['formset'] = LimitedInlineFormset
            yield inline.get_formset(request, obj, **kwargs)
