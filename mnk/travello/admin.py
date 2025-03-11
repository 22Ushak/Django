from django.contrib import admin
from .models import Destination, Comments,IPVisit,CustomUser
# Register your models here.
admin.site.register(Destination)
admin.site.register(Comments)
admin.site.register(IPVisit)
admin.site.register(CustomUser)
