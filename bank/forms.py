from django import forms

from Company.models import Company
from bank.models import Mailbank, BankAccount, Bank


class BankAccountForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), label='Компания')
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), label='Банк')
    login_bank = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите логин акаунта'}), label='Логин')
    password_bank = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите пароль аккаунта'}),
                                    label='Пароль')

    class Meta:
        model = BankAccount
        fields = ['company', 'bank', 'login_bank', 'password_bank']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"


class MailForms(forms.ModelForm):
    class Meta:
        model = Mailbank

        fields = [
            'publication_mail'
        ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object['publication_mail'] = False
        self.object.save()
        return super().form_valid(form)
