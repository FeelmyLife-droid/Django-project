from django import forms
from bank.models import Mailbank


class MailForms(forms.ModelForm):
    class Meta:
        model = Mailbank

        fields = [
            'publication_mail'
        ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object['publication_mail']=False
        self.object.save()
        return super().form_valid(form)
