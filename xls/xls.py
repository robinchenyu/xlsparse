# -*- encoding:utf-8 -*-
__author__ = 'Cheny'

from django.conf.urls import patterns, url
from .views import upload_xls


urlpatterns = patterns('',
                       url(r'^$', upload_xls, name='upload_xls'),
)
