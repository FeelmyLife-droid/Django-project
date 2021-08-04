from django import forms
from django.forms import IntegerField

from Director.models import Director


class DateInput(forms.DateInput):
    input_type = 'date'


class DirectorsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите ФИО'}), label='Фамилия Имя Отчество')
    inn = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите ИНН'}), label='ИНН')
    date_of_birth = forms.DateField(widget=DateInput(), label='Дата рождения')
    id_passport = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Введите Номер паспорта'}),
                                     label='Номер паспорта')
    date_of_issue = forms.DateField(widget=DateInput(), label='Дата выдачи')
    issued_by = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите Кем выдан'}), label='Кем выдан')
    department_сode = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Введите Код подразделения'}),
                                         label='Код подразделения')
    street = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите Улицу'}), label='Улица')
    house = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'Введите Дом'}), label='Дом')

    class Meta:
        model = Director
        fields = ['name', 'inn', 'date_of_birth', 'id_passport', 'date_of_issue', 'issued_by', 'department_сode',
                  'street', 'house']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"