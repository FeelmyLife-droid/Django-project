from django.urls import path

from bank.views import BankViews

app_name = 'bank'

urlpatterns = [
    path('', BankViews.as_view(), name='bank'),
]
