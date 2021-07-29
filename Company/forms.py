from django import forms
from Company.models import Company


class CompanyForms(forms.ModelForm):
    class Meta:
        model = Company

        fields = [
            'name',
            'inn',
            'okved',
            'legal_address',
            'date_of_application',
            'registration_date',
            'charter_number',
            'email',
            'directors',
        ]
