from django.conf.urls import patterns, include, url
from django.contrib import admin
from api.views import *

urlpatterns = patterns('',
                       url(r'^verify', VerifyCodeView.as_view()),
                       url(r'^register', UserRegisterView.as_view()),
                       url(r'^third_register', UserThirdRegisterView.as_view()),
                       url(r'^third_login', UserThirdLoginView.as_view()),
                       url(r'^password/forget', UserResetView.as_view()),
                       url(r'^password/change', UserChangePasswordView.as_view()),
                       url(r'^login', UserLoginView.as_view()),
                       url(r'^logout', UserLogoutView.as_view()),
                       url(r'^bind', UserThirdAccountBindView.as_view()),
                       url(r'^avatar', UserAvatarView.as_view()),
                       url(r'^upload', AvatarView.as_view()),

                       url(r'^match', MatchView.as_view()),
                       url(r'^check', CheckMatchView.as_view()),
                       url(r'^leave', LeaveRoomView.as_view()),
                       url(r'^status', RoomStatusView.as_view()),
                       url(r'^open', OpenTimeView.as_view()),
                       url(r'^number', MatchNumberView.as_view()),
                       url(r'^modify', ModifyInfoView.as_view()),
                       url(r'^report', UserFeedBackView.as_view()),
                       )
