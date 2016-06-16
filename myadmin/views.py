# coding: utf-8
from __future__ import unicode_literals

import requests
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response

# Create your views here.
from django.views.generic import UpdateView, TemplateView, ListView, RedirectView

from core.models import *
from myadmin.forms import AdminLoginForm
from myadmin.models import FAdmin
from core.Mixin.CheckMixin import CheckAdminPagePermissionMixin


class AdminView(UpdateView):
    model = FAdmin
    form_class = AdminLoginForm
    http_method_names = ['get']
    success_url = '/admin/index'

    def get(self, request, *args, **kwargs):
        token = request.session.get('token')
        if token:
            if FAdmin.objects.filter(token=token).exists():
                return HttpResponseRedirect('/admin/index')
        return render_to_response('admin/admin_login.html')


class AdminIndexView(CheckAdminPagePermissionMixin, TemplateView):
    model = FAdmin
    http_method_names = ['get']
    template_name = 'admin/admin_index.html'

    def get(self, request, *args, **kwargs):
        return super(AdminIndexView, self).get(request, *args, **kwargs)


class AdminPlayerListView(CheckAdminPagePermissionMixin, ListView):
    model = ChatHistory
    template_name = 'admin/admin_history.html'
    paginate_by = 20


class AdminUserListView(CheckAdminPagePermissionMixin, ListView):
    model = FaceUser
    template_name = 'admin/admin_users.html'
    paginate_by = 20


class AdminSettingView(CheckAdminPagePermissionMixin, TemplateView):
    template_name = 'admin/admin_setting.html'
    http_method_names = ['get']


class AdminLogoutView(CheckAdminPagePermissionMixin, RedirectView):
    url = '/admin/login'


class PeepView(CheckAdminPagePermissionMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        return render_to_response('admin/interface_Waiting.html')


class ReportView(CheckAdminPagePermissionMixin, TemplateView):
    template_name = 'admin/admin_report.html'
    http_method_names = ['get']
