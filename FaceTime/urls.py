from django.conf.urls import patterns, include, url
from django.contrib import admin

from FaceTime import settings
from api.views import PortocolView

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'FaceTime.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^site_admin/', include(admin.site.urls)),
                       url(r'^protocol/', PortocolView.as_view()),
                       url(r'^api/v1/', include('api.urls')),
                       url(r'^admin/api/', include('myadmin.api_urls')),
                       url(r'^admin/', include('myadmin.urls')),
                       url(r'^s/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_MEDIA}),
                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_MEDIA}),
                       )
