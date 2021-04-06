from django.contrib import admin

from Company.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'directors', 'legal_city', 'registration_date',)


admin.site.register(Company, CompanyAdmin)
