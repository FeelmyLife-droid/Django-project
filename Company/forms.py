from django import forms
from Company.models import Company


class CompanyForms(forms.ModelForm):
    class Meta:
        model = Company

        fields = [
            '__all__'
        ]
