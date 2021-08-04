from datetime import date

from django.db import models


class Director(models.Model):
    name = models.CharField(max_length=255, verbose_name='ФИО')
    inn = models.CharField(max_length=30, verbose_name='ИНН')
    date_of_birth = models.DateField(default=date.today, verbose_name='Дата рождения')
    place_of_birth = models.CharField(max_length=255, verbose_name='Место рождения')
    id_passport = models.CharField(max_length=10, verbose_name='Номер паспорта')
    date_of_issue = models.CharField(max_length=10, verbose_name='Дата выдачи')
    issued_by = models.CharField(max_length=255, verbose_name='Кем выдан')
    department_сode = models.CharField(max_length=7, verbose_name='Код подразделения')
    street = models.CharField(max_length=255, verbose_name='Улица')
    house = models.CharField(max_length=255, verbose_name='Дом')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Директор'
        verbose_name_plural = 'Директора'

    def save(self, *args, **kwargs):

        self.name = self.name.title()
        super().save(*args, **kwargs)
