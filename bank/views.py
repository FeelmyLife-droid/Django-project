from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Sum, Min, Count
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView

from Company.models import Company
from bank.forms import MailForms
from bank.models import BankAccount, Bank, Mailbank


class BankViews(ListView):
    model = BankAccount
    template_name = 'bank/bank.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        date = datetime.today() - timedelta(days=1)

        context = {
            'companies': Company.objects.all().order_by('id'),
            'banks': Bank.objects.all().order_by('id'),
            'bank_accounts': BankAccount.objects.all().order_by('company_id'),
            'balance': BankAccount.objects.aggregate(balance=Sum('balance', decimal_places=2),
                                                     date_updated=Min('date_updated')),
            'all_balance': BankAccount.objects.values('bank__name').order_by('bank_id').annotate(total=Sum('balance'),
                                                                                                 date_updated=Min(
                                                                                                     'date_updated')),
            'bal_firm': BankAccount.objects.values('company__name').order_by('company_id').annotate(
                total=Sum('balance')),
            'date_error': BankAccount.objects.filter(date_updated__startswith=date.date()).select_related('company',
                                                                                                          'bank'),
            'mail_accounts': Mailbank.objects.values('account_id').order_by('account_id').annotate(
                count=Count('id', filter=Q(publication_mail=True)),
            )
        }
        print(context['mail_accounts'])

        return context


class BankAll(ListView):
    model = BankAccount
    context_object_name = 'latest_articles'
    template_name = "bank/bank_all.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['all_list'] = BankAccount.objects.select_related('company', 'bank').order_by('-date_updated').all()
        return context


class BankAdd(CreateView):
    model = BankAccount
    template_name = "bank/bank_form.html"
    fields = '__all__'

    def get_success_url(self):
        return reverse('bank:bank')


class BankMailAccount_update(UpdateView):
    model = Mailbank
    form_class = MailForms


class BankMailAccount(ListView):
    model = Mailbank
    template_name = 'bank/mail_account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = context['object_list'][0]
        return context

    def get_queryset(self):
        return Mailbank.objects.filter(account_id=self.kwargs['pk'])
