from django.db.models import Sum, Min
from django.views.generic import ListView

from Company.models import Company
from bank.models import BankAccount


class BankViews(ListView):
    model = BankAccount
    template_name = 'bank/bank.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.all()
        context['bankAccounts'] = BankAccount.objects.select_related('company', 'bank').order_by('bank_id')
        context['balance'] = BankAccount.objects.aggregate(balance=Sum('balance', decimal_places=2))

        return context

    def get_queryset(self):
        return BankAccount.objects.values('bank__name', 'bank__id').order_by('bank_id').annotate(
            total=Sum('balance'), date_updated=Min('date_updated'))
