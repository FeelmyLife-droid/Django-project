from django.db.models import Sum
from django.views.generic import ListView, TemplateView, DetailView

from Company.models import Company
from Director.models import Director
from bank.models import BankAccount
from datetime import date

from test import check_age


class DirectorViews(ListView):
    model = Director
    context_object_name = 'latest_articles'
    template_name = "Director/directors.html"


class HomeViews(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = BankAccount.objects.aggregate(balance=Sum('balance', decimal_places=2))
        print(context['balance'])
        return context


class DirectorDetail(DetailView):
    model = Director
    template_name = "Director/director_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['age'] = check_age(self.object.date_of_birth)
        context['firms'] = Company.objects.filter(directors_id=self.object.pk)
        # print(context['firms'])
        print(context['age'])
        return context
