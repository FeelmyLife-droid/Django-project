from django import forms
import datetime

from Company.models import Company
from Director.models import Director


class DateInput(forms.DateInput):
    input_type = 'date'


class CompanyForms(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите название фирмы'}))
    inn = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите ИНН фирмы'}), max_length=10)
    okved = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите оквэд фирмы'}))
    legal_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите адресс'}))
    date_of_application = forms.DateField(widget=DateInput())
    registration_date = forms.DateField(widget=DateInput())
    charter_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите номер устава фирмы'}))
    directors = forms.ModelChoiceField(queryset=Director.objects.all())

    class Meta:
        model = Company
        fields = ['name', 'inn', 'okved', 'legal_address', 'date_of_application', 'registration_date', 'charter_number',
                  'directors']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
