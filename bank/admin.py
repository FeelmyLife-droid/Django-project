from django.contrib import admin

from bank.models import Bank, BankAccount, Mailbank


class BankAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('company', 'bank', 'date_created', 'date_updated', 'balance')


class MailbankAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_mail', 'title_mail', 'content_mail', 'sender_mail','account_id','publication_mail')


admin.site.register(Bank, BankAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Mailbank, MailbankAdmin)
