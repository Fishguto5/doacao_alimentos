from django.contrib import admin

# Register your models here.
from django.contrib import admin
from core.models import Person

admin.site.register(Person)