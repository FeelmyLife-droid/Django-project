from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView

from Company.models import Company
from Director.models import Director

from Director.utils import check_age


class DirectorViews(ListView):
    model = Director
    context_object_name = 'latest_articles'
    template_name = "Director/directors.html"


class DirectorAdd(CreateView):
    model = Director
    template_name = "Director/director_form.html"
    fields = '__all__'

    def get_success_url(self):
        return reverse('directors:directors')


class DirectorDetail(DetailView):
    model = Director
    template_name = "Director/director_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['age'] = check_age(self.object.date_of_birth)
        context['firms'] = Company.objects.filter(directors_id=self.object.pk)
        return context
