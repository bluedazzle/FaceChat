from django.conf.urls import patterns, include, url
from myadmin.api_views import *

urlpatterns = patterns('',
                       url(r'^login', AdminLoginView.as_view()),
                       url(r'^logout', AdminLogoutView.as_view()),
                       url(r'^index', AdminIndexView.as_view()),
                       url(r'^admin', AdminUserView.as_view()),
                       url(r'^user/(?P<uid>(\d)+)/forbid', AdminUserForbidView.as_view()),
                       url(r'^user/(?P<uid>(\d)+)', AdminUserDetailView.as_view()),
                       url(r'^users', AdminUserListView.as_view()),
                       # url(r'^player/(?P<pid>(\d)+)', AdminPlayerDetailView.as_view()),
                       url(r'^chat', AdminChatHistoryView.as_view()),
                       url(r'^report/(?P<rid>(\d)+)', HandleReportView.as_view()),
                       url(r'^reports', ReportListView.as_view()),


                       )
