from django.contrib import admin

import models

class FacebookUserAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user')
    search_fields = ('uid', 'user__email')


admin.site.register(models.FacebookUser, FacebookUserAdmin)
