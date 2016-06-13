# coding: utf-8
from __future__ import unicode_literals

import json
import random
import string

import datetime

from django.db.models import Q
from django.utils.timezone import get_current_timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View

from core.Mixin.CheckMixin import CheckSecurityMixin, CheckTokenMixin
from core.Mixin.StatusWrapMixin import *
from core.dss.Mixin import MultipleJsonResponseMixin, FormJsonResponseMixin, JsonResponseMixin

from core.sms import send_sms
from core.utils import upload_picture, save_image
from core.models import *
from api.forms import VerifyCodeForm, UserRegisterForm, UserResetForm, UserLoginForm, UserChangePasswordForm, \
    UserThirdRegisterForm
import time


class VerifyCodeView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    form_class = VerifyCodeForm
    http_method_names = ['post', 'get']
    success_url = 'localhost'
    count = 6

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        code = request.GET.get('code', '')
        if phone and code:
            verify_list = Verify.objects.filter(phone=unicode(phone)).order_by('-create_time')
            if verify_list.exists():
                verify = verify_list[0]
                now_time = datetime.datetime.now(tz=get_current_timezone())
                if now_time - verify.create_time > datetime.timedelta(minutes=30):
                    self.status_code = INFO_EXPIRE
                    self.message = '验证码已过期, 请重新获取'
                    verify.delete()
                    return self.render_to_response(dict())
                if verify.code != unicode(code):
                    self.status_code = ERROR_VERIFY
                    self.message = '验证码不正确'
                    return self.render_to_response(dict())
                verify.delete()
                return self.render_to_response(dict())
            else:
                self.status_code = INFO_NO_VERIFY
                self.message = '请获取验证码'
                return self.render_to_response(dict())
        self.status_code = ERROR_DATA
        self.message = '数据缺失'
        return self.render_to_response(dict())

    def post(self, request, *args, **kwargs):
        reg = request.POST.get('reg', True)
        if reg == 'false':
            reg = False
        if reg:
            return super(VerifyCodeView, self).post(request, *args, **kwargs)
        form = Verify()
        setattr(form, 'cleaned_data', {'phone': request.POST.get('phone')})
        setattr(form, 'reg', reg)
        self.object = Verify(phone=request.POST.get('phone'))
        return self.form_valid(form)

    def form_valid(self, form):
        if not hasattr(form, 'reg'):
            super(VerifyCodeView, self).form_valid(form)
        verify = self.create_verify_code()
        if send_sms(verify, form.cleaned_data.get('phone')):
            self.object.code = verify
            self.object.save()
            return self.render_to_response(dict())
        self.status_code = ERROR_UNKNOWN
        self.message = '短信发送失败,请重试'
        return self.render_to_response(dict())

    def form_invalid(self, form):
        super(VerifyCodeView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def create_verify_code(self):
        return string.join(
            random.sample('1234567890', self.count)).replace(" ", "")


class UserRegisterView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    form_class = UserRegisterForm
    http_method_names = ['post']
    success_url = 'localhost'
    datetime_type = 'timestamp'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind', 'qq_bind',
                    'sex']
    count = 64
    token = ''

    def form_valid(self, form):
        # code = Invite.objects.filter(code__iexact=unicode(form.cleaned_data.get('code')))
        # # if code.exists():
        # #     code = code[0]
        #     if not code.use:
        super(UserRegisterView, self).form_valid(form)
        self.token = self.create_token()
        self.object.token = self.token
        self.object.avatar = form.cleaned_data.get('avatar')
        self.object.sex = form.cleaned_data.get('sex')
        self.object.set_password(form.cleaned_data.get('password'))
        self.object.save()
        # code.use = True
        # code.belong = self.object
        # code.save()
        return self.render_to_response(self.object)
        # else:
        #     self.message = '邀请码已使用'
        #     self.status_code = ERROR_DATA
        # return self.render_to_response(dict())
        # else:
        #     self.message = '邀请码不存在'
        #     self.status_code = ERROR_DATA
        #     return self.render_to_response(dict())

    def form_invalid(self, form):
        super(UserRegisterView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")


class UserThirdRegisterView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, CreateView):
    model = FaceUser
    form_class = UserThirdRegisterForm
    http_method_names = ['post']
    success_url = 'localhost'
    datetime_type = 'timestamp'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind', 'qq_bind',
                    'sex']
    count = 64

    def form_valid(self, form):
        # code = Invite.objects.filter(code__iexact=form.cleaned_data.get('code'))
        # if code.exists():
        #     code = code[0]
        #     if not code.use:
        super(UserThirdRegisterView, self).form_valid(form)
        t_type = form.cleaned_data.get('type')
        if t_type == 1:
            self.object.wechat_openid = form.cleaned_data.get('openid')
            self.object.wechat_bind = True
        elif t_type == 2:
            self.object.weibo_openid = form.cleaned_data.get('openid')
            self.object.weibo_bind = True
        elif t_type == 3:
            self.object.qq_openid = form.cleaned_data.get('openid')
            self.object.qq_bind = True
        status, path = save_image(form.cleaned_data.get('avatar'),
                                  name='avatar{0}.jpg'.format(unicode(time.time()).replace('.', '')))
        if status:
            self.object.avatar = path
        self.token = self.create_token()
        self.object.token = self.token
        self.object.set_password(form.cleaned_data.get('password'))
        self.object.save()
        # code.use = True
        # code.belong = self.object
        # code.save()
        return self.render_to_response(self.object)
        #     else:
        #         self.message = '邀请码已使用'
        #         self.status_code = ERROR_DATA
        #     return self.render_to_response(dict())
        # else:
        #     self.message = '邀请码不存在'
        #     self.status_code = ERROR_DATA
        #     return self.render_to_response(dict())

    def form_invalid(self, form):
        super(UserThirdRegisterView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")


class UserResetView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, UpdateView):
    form_class = UserResetForm
    model = FaceUser
    http_method_names = ['post']
    success_url = 'localhost'
    datetime_type = 'timestamp'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind', 'qq_bind']
    pk_url_kwarg = 'phone'
    count = 64
    token = ''

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def form_invalid(self, form):
        super(UserResetView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def form_valid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserResetView, self).form_valid(form)
        self.token = self.create_token()
        self.object.token = self.token
        self.object.set_password(form.cleaned_data.get('password'))
        self.object.save()
        return self.render_to_response(self.object)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.request.POST.get(self.pk_url_kwarg, None)
        queryset = queryset.filter(phone=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            self.message = '帐号不存在'
            self.status_code = INFO_NO_EXIST
            return None
        return obj


class UserLoginView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, UpdateView):
    model = FaceUser
    form_class = UserLoginForm
    count = 64
    http_method_names = ['post']
    pk_url_kwarg = 'phone'
    datetime_type = 'timestamp'
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind',
                    'qq_bind', 'sex']
    success_url = 'localhost'
    token = ''

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def form_invalid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserLoginView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def form_valid(self, form):
        if not self.object:
            return self.render_to_response(dict())
        super(UserLoginView, self).form_valid(form)
        if not self.object.check_password(form.cleaned_data.get('password')):
            self.message = '密码不正确'
            self.status_code = ERROR_PASSWORD
            return self.render_to_response(dict())
        self.token = self.create_token()
        # self.object.set_password(form.cleaned_data.get('password'))
        self.object.token = self.token
        self.object.save()
        return self.render_to_response(self.object)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.request.POST.get(self.pk_url_kwarg, None)
        queryset = queryset.filter(phone=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            self.message = '帐号不存在'
            self.status_code = INFO_NO_EXIST
            return None
        return obj


class UserLogoutView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, View):
    http_method_names = ['get']
    count = 64

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        self.user.token = self.create_token()
        self.user.save()
        return self.render_to_response(dict())


class UserChangePasswordView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, UpdateView):
    http_method_names = ['post']
    model = FaceUser
    success_url = 'localhost'
    form_class = UserChangePasswordForm

    def get_object(self, queryset=None):
        self.object = self.user
        return self.user

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        return super(UserChangePasswordView, self).post(request, *args, **kwargs)

    def form_invalid(self, form):
        super(UserChangePasswordView, self).form_invalid(form)
        self.status_code = ERROR_DATA
        self.message = json.loads(form.errors.as_json()).values()[0][0].get('message')
        return self.render_to_response(dict())

    def form_valid(self, form):
        super(UserChangePasswordView, self).form_valid(form)
        return self.render_to_response(dict())

    def get_form_kwargs(self):
        kwargs = super(UserChangePasswordView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs


class UserThirdAccountBindView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    model = FaceUser

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        t_type = request.POST.get('type')
        open_id = request.POST.get('openid')
        users = FaceUser.objects.filter(Q(wechat_openid=open_id) | Q(weibo_openid=open_id) | Q(qq_openid=open_id))
        if users.exists():
            self.message = '该账号已绑定,请直接登陆'
            self.status_code = INFO_EXISTED
            return self.render_to_response(dict())
        if t_type and open_id:
            if t_type == '1':
                self.user.wechat_openid = open_id
                self.user.wechat_bind = True
            elif t_type == '2':
                self.user.weibo_openid = open_id
                self.user.weibo_bind = True
            elif t_type == '3':
                self.user.qq_openid = open_id
                self.user.qq_bind = True
            self.user.save()
            return self.render_to_response(dict())
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


class UserThirdLoginView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    include_attr = ['token', 'id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind',
                    'qq_bind', 'sex']
    datetime_type = 'timestamp'
    model = FaceUser
    count = 64

    def get(self, request, *args, **kwargs):
        openid = request.GET.get('openid')
        if openid:
            user = FaceUser.objects.filter(Q(weibo_openid=openid) | Q(wechat_openid=openid) | Q(qq_openid=openid))
            if user.exists():
                token = self.create_token()
                user = user[0]
                user.token = token
                user.save()
                return self.render_to_response(user)
            self.message = '三方帐号未绑定'
            self.status_code = INFO_NO_EXIST
            return self.render_to_response(dict())
        self.message = '参数缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())

    def create_token(self):
        return string.join(
            random.sample('ZYXWVUTSRQPONMLKJIHGFEDCBA1234567890zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgfedcba',
                          self.count)).replace(" ", "")


class UserAvatarView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']
    include_attr = ['id', 'create_time', 'nick', 'phone', 'avatar', 'wechat_bind', 'weibo_bind', 'qq_bind']
    datetime_type = 'timestamp'
    model = FaceUser

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        avatar = request.FILES.get('avatar')
        if avatar:
            s_path, full_path = upload_picture(avatar)
            self.user.avatar = s_path
            self.user.save()
            return self.render_to_response(self.user)
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


class AvatarView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        avatar = request.FILES.get('avatar')
        if avatar:
            s_path, full_path = upload_picture(avatar)
            return self.render_to_response({'url': s_path})
        self.message = '数据缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response(dict())


class MatchView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    include_attr = ['room_id', 'matcher', 'nick', 'avatar', 'id', 'chat', 'uuid', 'sex']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        wish = int(request.GET.get('wish'))
        match_list = Match.objects.exclude(user=self.user)
        print match_list
        if wish != 2:
            match_list = match_list.filter(sex=wish)
        print match_list
        match_list = match_list.filter(Q(wish=self.user.sex) | Q(wish=2))
        if match_list.exists():
            index = random.randint(0, (match_list.count() - 1))
            match = match_list[index]
            chat = ChatHistory.objects.filter(creater_uuid=match.uuid, chat=True)
            matcher = {'nick': match.user.nick,
                       'avatar': match.user.avatar,
                       'id': match.user_id,
                       'sex': match.user.sex}
            match.delete()
            if chat.exists():
                chat = chat[0]
                if not chat.receiver:
                    chat.receiver = self.user
                    chat.save()
                    return self.render_to_response({'room_id': chat.uuid,
                                                    'matcher': matcher})
                else:
                    self.status_code = INFO_EXISTED
                    self.message = '匹配房间被占用'
                    return self.render_to_response({})
            else:
                self.status_code = INFO_NO_EXIST
                self.message = '匹配房间不存在'
                return self.render_to_response({})
        else:
            match_list = Match.objects.filter(user=self.user)
            if match_list.exists():
                chat = ChatHistory.objects.filter(creater_uuid=match_list[0].uuid)
                if chat.exists():
                    chat = chat[0]
                    chat.chat = False
                    chat.save()
                match_list[0].delete()
            new_match = Match(user=self.user, wish=wish, sex=self.user.sex)
            uuid = self.create_uuid('M')
            new_match.uuid = uuid
            new_match.save()
            cuuid = self.create_uuid()
            chat = ChatHistory(chat=True, uuid=cuuid, creater=self.user, creater_uuid=uuid)
            chat.save()
            self.status_code = INFO_NO_MATCH
            self.message = '暂无匹配'
            return self.render_to_response({'chat': chat})

    def create_uuid(self, sign='C'):
        return '{0}{1}{2}'.format(sign, unicode(time.time()).replace('.', '')[:12], random.randint(100000, 999999))


class CheckMatchView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    include_attr = ['room_id', 'matcher', 'nick', 'avatar', 'id', 'sex']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        room_id = request.GET.get('room_id')
        room = ChatHistory.objects.filter(uuid=room_id)
        if room.exists():
            room = room[0]
            if not room.chat:
                self.status_code = INFO_ROOM_DESTROY
                self.message = '房间已过期'
                return self.render_to_response({})
            if room.receiver:
                return self.render_to_response({'room_id': room.uuid,
                                                'matcher': room.receiver})
            self.status_code = INFO_NO_EXIST
            self.message = '暂无匹配'
            return self.render_to_response({})
        self.status_code = ERROR_DATA
        self.message = '房间不存在'
        return self.render_to_response({})


class LeaveRoomView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        room_id = request.GET.get('room_id')
        room = ChatHistory.objects.filter(uuid=room_id)
        if room.exists():
            room = room[0]
            room.chat = False
            room.save()
            return self.render_to_response({})
        self.message = '房间不存在'
        self.status_code = ERROR_DATA
        return self.render_to_response({})


class RoomStatusView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    include_attr = ['chat', 'id', 'uuid']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        room_id = request.GET.get('room_id')
        room = ChatHistory.objects.filter(uuid=room_id)
        if room.exists():
            room = room[0]
            return self.render_to_response(room)
        self.status_code = ERROR_DATA
        self.message = '房间不存在'
        return self.render_to_response({})


class OpenTimeView(CheckSecurityMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']
    include_attr = ['start_time', 'end_time']

    def get(self, request, *args, **kwargs):
        open_time = Setting.objects.all()[0]
        open = False
        now_time = datetime.datetime.now(tz=get_current_timezone()).time().replace(microsecond=0)
        if open_time.start_time <= now_time <= open_time.end_time:
            open = True
        return self.render_to_response({'open': open,
                                        'detail': open_time})


class MatchNumberView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        number = ChatHistory.objects.all().count()
        return self.render_to_response({'number': number})


class ModifyInfoView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not self.wrap_check_sign_result():
            return self.render_to_response(dict())
        if not self.wrap_check_token_result():
            return self.render_to_response(dict())
        sex = request.POST.get('sex')
        nick = request.POST.get('nick')
        if sex and nick:
            user = FaceUser.objects.filter(nick=nick)
            if user.exists():
                user = user[0]
                if user != self.user:
                    self.message = '昵称已存在'
                    self.status_code = INFO_EXISTED
                    return self.render_to_response({})
            self.user.sex = sex
            self.user.nick = nick
            self.user.save()
            return self.render_to_response({})
        self.message = '信息缺失'
        self.status_code = ERROR_DATA
        return self.render_to_response({})

# class UserFeedBackView(CheckSecurityMixin, CheckTokenMixin, StatusWrapMixin, JsonResponseMixin, DetailView):
#     http_method_names = ['post']
#     model = FeedBack
#
#     def post(self, request, *args, **kwargs):
#         if not self.wrap_check_sign_result():
#             return self.render_to_response(dict())
#         if not self.wrap_check_token_result():
#             return self.render_to_response(dict())
#         content = request.POST.get('content')
#         if content and content != '':
#             FeedBack(content=content, author=self.user).save()
#             return self.render_to_response(dict())
#         self.message = '请填写反馈内容'
#         self.status_code = ERROR_DATA
#         return self.render_to_response(dict())
