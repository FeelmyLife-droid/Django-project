from django.contrib import admin

from Director.models import Director


class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'id_passport',)


admin.site.register(Director, DirectorAdmin)
