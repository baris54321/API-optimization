from django.contrib import admin

# Register your models here.

from .models import AppUser, AppPost, AppComment

admin.site.register(AppUser)
admin.site.register(AppPost)
admin.site.register(AppComment)