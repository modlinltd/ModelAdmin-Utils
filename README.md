ModelAdmin-Mixins
=================

A collection of useful django admin.ModelAdmin mixins

## LocationMixin

### Intro
Before Django 1.6 introduced [ModelAdmin.preserve_filters][1] the bahavior
of Django admin was as follows:

1. filter a changelist by using search/filters
2. click one of the result entries
3. edit the result and save it
4. Django redirects you to the changelist without storing your filters

This mixin introduces the ability to redirect the client back to the changelist
with the filters restored, after saving the changeform.

### Usage
Simply import LocationMixin and place it as a parent class on any ModelAdmin sub-class, see TestLocationAdmin in admin.py for an example.

## GenericSearchMixin

### Intro
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

### Examples (see more in admin.py):

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

### Notes:
* Required Django > 1.6
* Currently assumes id of related objects are unique across all models

[1]: https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.preserve_filters
