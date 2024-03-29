# coding: utf-8

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import BaseModel


class FAdmin(BaseModel, AbstractBaseUser):
    phone = models.CharField(max_length=13, unique=True)
    nick = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=64, unique=True)

    USERNAME_FIELD = 'phone'

    def __unicode__(self):
        return '{0}-{1}'.format(self.phone, self.nick)
