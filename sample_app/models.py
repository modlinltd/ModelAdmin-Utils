from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

owner_types = Q(model='person') | Q(model='carlot')


class Car(models.Model):
    model = models.CharField(max_length=32)

    content_type = models.ForeignKey(ContentType,
                                     limit_choices_to=owner_types)
    object_id = models.CharField(max_length=32)
    owner = generic.GenericForeignKey('content_type', 'object_id')


class Person(models.Model):
    name = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)


class CarLot(models.Model):
    name = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)
