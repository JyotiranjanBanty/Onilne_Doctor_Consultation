from django.contrib import admin

# Register your models here.
from app.models import *
admin.site.register(Profile)
admin.site.register(Doctor)
admin.site.register(Appointment)