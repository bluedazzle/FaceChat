# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


# Create your models here.


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FaceUser(BaseModel, AbstractBaseUser):
    sex_choice = {
        (0, '女'),
        (1, '男')
    }

    nick = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    sex = models.IntegerField(default=0, choices=sex_choice)
    avatar = models.CharField(max_length=256, default='/s/image/avatar.png')

    forbid = models.BooleanField(default=False)
    wechat_openid = models.CharField(max_length=64, null=True, blank=True, unique=True)
    wechat_bind = models.BooleanField(default=False)
    weibo_openid = models.CharField(max_length=64, null=True, blank=True, unique=True)
    weibo_bind = models.BooleanField(default=False)
    qq_openid = models.CharField(max_length=64, null=True, blank=True, unique=True)
    qq_bind = models.BooleanField(default=False)

    token = models.CharField(max_length=64, unique=True)

    USERNAME_FIELD = 'phone'

    def __unicode__(self):
        return '{0}-{1}'.format(self.nick, self.phone)


class Match(BaseModel):
    sex_choice = {
        (0, '女'),
        (1, '男'),
        (2, '均可')
    }

    wish = models.IntegerField(default=0, choices=sex_choice)
    sex = models.IntegerField(default=0, choices=sex_choice)
    user = models.ForeignKey(FaceUser, unique=True, related_name='user_matches')
    uuid = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return '{0}-{1}->{2}'.format(self.user.nick, self.sex, self.wish)


class ChatHistory(BaseModel):
    creater = models.ForeignKey(FaceUser, related_name='user_create_chats', null=True, blank=True,
                                on_delete=models.SET_NULL)
    creater_uuid = models.CharField(max_length=64, unique=True)
    receiver = models.ForeignKey(FaceUser, related_name='user_receive_chats', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    uuid = models.CharField(max_length=64, unique=True)
    chat = models.BooleanField(default=True)

    def __unicode__(self):
        if self.receiver:
            return '{0}-{1}'.format(self.creater.nick, self.receiver.nick)
        else:
            return '{0}-{1}'.format(self.creater.nick, '无')


class Setting(BaseModel):
    start_time = models.TimeField()
    end_time = models.TimeField()
    remark = models.CharField(default='ios', max_length=20)

    def __unicode__(self):
        return self.remark


class Verify(BaseModel):
    code = models.CharField(max_length=10)
    phone = models.CharField(max_length=13)

    def __unicode__(self):
        return self.phone


class Secret(BaseModel):
    secret = models.CharField(max_length=64)
    info = models.CharField(max_length=20, default='system')

    def __unicode__(self):
        return self.info
