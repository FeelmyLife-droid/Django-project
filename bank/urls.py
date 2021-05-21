from django.urls import path

from bank.views import BankViews, BankAdd, BankAll

app_name = 'bank'

urlpatterns = [
    path('', BankViews.as_view(), name='bank'),
    path('add_bank/', BankAdd.as_view(), name='bank_add'),
    path('all_bank/', BankAll.as_view(), name='bank_all'),
]
