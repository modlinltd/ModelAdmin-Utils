ModelAdmin-Utils
================

A collection of useful django `admin.ModelAdmin` mixins and template tags

Installation
============

    pip install django-modeladmin-utils

LimitInlinesAdminMixin
======================

Intro
-----
Occasionally, a relation to a specified object may include quite a few object. In this case, a large list of inlines will be rendered, which may not be desired.

### Usage
Simply add LimitInlinesAdminMixin to the parent ModelAdmin, and specify the inlines to be limited in the attribute `limit_inlines`. The number of entries shown is determined by `settings.INLINES_MAX_LIMIT` (defaults to 15).

    from modeladmin_utils.mixins import LimitInlinesAdminMixin

    # ...

    class SomeParentModelAdmin(LimitInlinesAdminMixin, admin.ModelAdmin):
        inlines = (MyRelationInline, AnotherRelativeInline)
        limit_inlines = (MyRelationInline, )

Template: Link to "show all" entries
------------------------------------

Additionally to limiting, you may also display in the header of the inline container a link to related object changelist, filtered by related entries only. This is achievable by the use of a `templatetag` provided in this package. Overriding the admin templates for the relevant inline/s is easy:

    {% link_to_changelist inline_admin_formset original as changelist_url %}
    {% if changelist_url %}
        &nbsp;({{inline_admin_formset.formset.limited_count}} / {{inline_admin_formset.formset.total_count}} displayed - <a href="{{ changelist_url }}">{% trans "Detailed View" %}</a>)
    {% endif %}

Notes
-----

1. To use the `templatetag`, the app must be added to the `settings.INSTALLED_APPS`:

        INSTALLED_APPS += (
            'modeladmin_utils',
        )

2. Examples of modified templates of both stacked and tabular inlines, based on Django 1.4 templates, are provided in this package (in `templates/admin/edit_inlines`). However, these are not used by default to avoid confusion, to use them simply copy the template over, modify (see below in specific instructions) and set inline `template` attribute, e.g:

        class MyRelationInline(admin.TabularInline):
            template = 'path_to_your/templates/admin/edit_inlines/tabular.html'


3. While the related model for the changelist is automatically determined, you may also specify an alternative model by specifying the `unlimited_changelist_model` attribute on the inline. This is useful if the inline is for a "through model" but link should lead to the target model.

        class MyRelationInline(admin.TabularInline):
            unlimited_changelist_model = 'myapp.MyTargetModel'


### Customizing template example
to add the link to a stacked template, copy over your original templates/admin/edit_inline/stacked.py, and place the code above in the div.tabular-header like so (note that I'm using a [django-grappelli](sehmaschine/django-grappelli) template here):

    {% load modeladmin_links %}

    {# ... #}
    {% link_to_changelist inline_admin_formset original as changelist_url %}
    <div class="tabular-header">
    <h2 class="grp-collapse-handler">
        {% if inline_admin_formset.opts.title %}{{ inline_admin_formset.opts.title }}{% else %}{{ inline_admin_formset.opts.verbose_name_plural|capfirst }}{% endif %}
        {% if changelist_url %}
            &nbsp;({{inline_admin_formset.formset.limited_count}} / {{inline_admin_formset.formset.total_count}} displayed - <a href="{{ changelist_url }}">{% trans "Detailed View" %}</a>)
        {% endif %}
    </h2>
    {# ... #}

And for stacked, use template templates/admin/edit_inline/stacked.py:

    {% load modeladmin_links %}

    {# ... #}
    <h2 class="grp-collapse-handler">
        {% if inline_admin_formset.opts.title %}
            {{ inline_admin_formset.opts.title }}
        {% else %}
            {{ inline_admin_formset.opts.verbose_name_plural|capfirst }}
        {% endif %}
        {% if changelist_url %}
            &nbsp;({{inline_admin_formset.formset.limited_count}} / {{inline_admin_formset.formset.total_count}} displayed - <a href="{{ changelist_url }}">{% trans "Detailed View" %}</a>)
        {% endif %}
    </h2>
    {# ... #}

GenericSearchMixin
==================

Intro
-----

Django allows definition of GenericForeignKey, but does not allow to easily query through them (joins). Hence, doing something like search "through" a Generic FK is anything but straightforward.

Enter GenericSearchMixin!

This mixin, overrides the ModelAdmin.get_search_results method to allow searching through a generic relation fields.

For quick set up, simply use a GenericForeignKey field name as the prefix
in 'search_fields'.

E.g: for a field named 'related_to' you can use the following:
search_fields = ('related_to__fname', 'related_to__email', ...)

Optionally, you may define 'related_search_mapping' in the ModelAdmin
to explicitely define a generic field's object id and allowed content types
(useful to limit the content types - faster query).

Examples (see more in admin.py)
-------------------------------

    # find out pk and ctype fields using the virtual field
    related_search_mapping = {
        'my_generic_fkey': {} 
    }

    # the manual, "define everything" way
    related_search_mapping = {
        'my_generic_fkey': {
            'object_id': 'related_pk_field',
            'ctypes': 'content_type_field'
        } 
    }

Notes
-----

* Required Django > 1.6
* Currently assumes id of related objects are unique across all models

[1]: https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.preserve_filters


LocationMixin
=============

**Note:** Obsolete with newer Django versions

Intro
-----

Before Django 1.6 introduced [ModelAdmin.preserve_filters][1] the bahavior
of Django admin was as follows:

1. filter a changelist by using search/filters
2. click one of the result entries
3. edit the result and save it
4. Django redirects you to the changelist without storing your filters

This mixin introduces the ability to redirect the client back to the changelist
with the filters restored, after saving the changeform.

## Usage
Simply import LocationMixin and place it as a parent class on any ModelAdmin sub-class, see TestLocationAdmin in admin.py for an example.
