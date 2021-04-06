from django.db.models import Sum
from django.views.generic import ListView

from bank.models import BankAccount


class BankViews(ListView):
    model = BankAccount
    template_name = 'bank/bank.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = BankAccount.objects.aggregate(balance=Sum('balance', decimal_places=2))
        return context

    def get_queryset(self):
        return BankAccount.objects.values('bank__name').order_by('bank_id').annotate(total=Sum('balance'))
