from django.contrib import admin

from .models import Person, Car

from ..mixins.location import LocationMixin
from ..mixins.search import GenericSearchMixin


class PersonAdmin(LocationMixin,
                  admin.ModelAdmin):
    """ Demonstrate LocationMixin """


class CarAdmin(GenericSearchMixin,
               admin.ModelAdmin):
    """ Demonstrate GenericSearchMixin """


admin.site.register(Person, PersonAdmin)
admin.site.register(Car, CarAdmin)
