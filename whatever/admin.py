from django.contrib import admin

import models

class PredictionAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    list_display = ('competition','user', 'created_date','ordered_teams')
    search_fields = ('user__email',)
    
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'is_active', 'last_login', 'date_joined')
    list_filter = ('is_active','is_superuser')
    search_fields = ('first_name', 'last_name', 'email')

class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'close_date', 'competition_date')

class PositionAdmin(admin.ModelAdmin):
    list_display = ('position', 'date',)

class LeagueTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'ordered_teams', 'added')
    search_fields = ('added',)

class RegistrationProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'activation_key', 'activated')
    list_filter = ('activated',)
    search_fields = ('email', 'activation_key')

class TeamAdmin(admin.ModelAdmin):
    pass

class EmailMessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Prediction, PredictionAdmin)
admin.site.register(models.CustomUser, UserAdmin)
admin.site.register(models.LeagueTable, LeagueTableAdmin)
admin.site.register(models.RegistrationProfile, RegistrationProfileAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Position, PositionAdmin)
admin.site.register(models.EmailMessage, EmailMessageAdmin)
admin.site.register(models.Competition, CompetitionAdmin)
