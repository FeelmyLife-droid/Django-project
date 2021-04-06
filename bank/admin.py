from django.contrib import admin

from bank.models import Bank, BankAccount


class BankAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('company', 'bank', 'date_created', 'date_updated', 'balance')


admin.site.register(Bank, BankAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
