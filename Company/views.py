from django.db.models import Sum
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView

from Company.forms import CompanyForms
from Company.models import Company
from test import check_age


class CompanyViews(ListView):
    model = Company
    context_object_name = 'latest_articles'
    template_name = "Company/company.html"
    success_url = reverse_lazy('company')


class CompanyDetail(DetailView):
    model = Company
    template_name = "Company/company_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banki'] = self.object.company.filter(company_id=self.object.pk)
        context['age'] = check_age(self.object.directors.date_of_birth)
        context['balance'] = self.object.company.aggregate(balance=Sum('balance', decimal_places=2))

        return context


class CompanyAdd(CreateView):
    form_class = CompanyForms
    template_name = "Company/company_form.html"

    def get_success_url(self):
        return reverse('company:company')


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('company:company')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
