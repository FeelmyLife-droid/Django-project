from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone


class Bank(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название Банка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'


class BankAccount(models.Model):
    company = models.ForeignKey('Company.Company', null=True, on_delete=models.CASCADE, verbose_name='Фирма',
                                related_name='company')
    bank = models.ForeignKey('Bank', null=True, on_delete=models.CASCADE, verbose_name='Банк', related_name='bank')
    login_bank = models.CharField(max_length=255, verbose_name='Логин', null=False)
    password_bank = models.CharField(max_length=255, verbose_name='Пароль', null=False)

    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    in_block = models.BooleanField()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        return self

    def __str__(self):
        return f'{self.company.name + "|" + self.bank.name}'

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'
        ordering = ["bank_id"]


class Mailbank(models.Model):
    account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, verbose_name='Аккаунт',
                                related_name='bankaccounts')
    date_mail = models.DateTimeField(null=True)
    title_mail = models.CharField(max_length=255, null=True, verbose_name='Заголовок письма')
    content_mail = models.TextField(null=True)
    sender_mail = models.CharField(max_length=255, null=True, verbose_name='Отправитель')
    publication_mail = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.account}'

    def get_absolute_url(self):
        return '/'

    # def read_mail(self, id):
    #     mail = Mailbank.objects.get(id=id)
    #     mail.publication_mail = False
    #     mail.save()
    #     return
