from django.db import models

from Company.utils import slugify
from Director.models import Director


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название фирмы')
    slug = models.SlugField(max_length=100, verbose_name='Название на латинице',blank=True)
    inn = models.CharField(max_length=255, verbose_name='ИНН')
    okved = models.CharField(max_length=255, verbose_name='ОКВЭД')
    legal_address = models.CharField(max_length=255, verbose_name='Юр.Адресс')
    legal_city = models.CharField(max_length=255, verbose_name='Юр.Город')
    date_of_application = models.CharField(max_length=255, verbose_name='Дата подачи')
    registration_date = models.CharField(max_length=255, verbose_name='Дата регистрации')
    charter_number = models.CharField(max_length=50, verbose_name='Номер устава')
    email = models.EmailField(blank=True)
    directors = models.ForeignKey(Director, null=True, verbose_name='Директор', on_delete=models.CASCADE)
    bankaccount = models.ForeignKey('bank.BankAccount', null=True, blank=True, verbose_name='Банк',
                                    on_delete=models.CASCADE, related_name='bankaccount')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.email = str(self.slug) + str(self.inn[:-3:-1])+'@mailtorg.ru'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Фирма'
        verbose_name_plural = 'Фирмы'
