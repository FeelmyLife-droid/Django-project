from django.urls import path

from bank.views import BankViews, BankAdd, BankAll, BankMailAccount, BankMailAccount_update

app_name = 'bank'

urlpatterns = [
    path('', BankViews.as_view(), name='bank'),
    path('add_bank/', BankAdd.as_view(), name='bank_add'),
    path('all_bank/', BankAll.as_view(), name='bank_all'),
    path('mail_account/<int:pk>', BankMailAccount.as_view(), name='mail_account'),
    path('update_mail/<int:pk>', BankMailAccount_update.as_view(), name='mail_account_update'),

]
