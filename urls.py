# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from apps.emergency import views
# from apps.lens import lens
# , ModelAPI


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('blueapps.account.urls')),
    # 如果你习惯使用 Django 模板，请在 home_application 里开发你的应用，
    # 这里的 home_application 可以改成你想要的名字
    url(r'^', include('home_application.urls')),
    # 如果你习惯使用 mako 模板，请在 mako_application 里开发你的应用，
    # 这里的 mako_application 可以改成你想要的名字
    url(r'^mako/', include('mako_application.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # emergency项目
    url(r'^favicon.ico$', RedirectView.as_view(
        url='static/emergency/imgs/logo.svg')),

    # emergency项目 前端页面
    url(r"^$", views.Index.as_view()),
    url(r"^bigshow/$", views.BigShow.as_view()),
    url(r"^m/", views.mobile.Index.as_view()),
    # emergency项目 Websocket测试前端页面
    url(r"^ws$", views.Ws.as_view()),

    # emergency项目 Websocket API
    url(r'^ws/emergencyomnibusgroup/$', views.emergencyomnibusgroup),
    url(r'^ws/emergencyovertimegroup/$', views.emergencyovertimegroup),


    # emergency项目 lens封装的通用API
    url(r'^api/', include('apps.urls')),


    # emergency项目 HTTP测试API
    url(r'^api/test/fault/$', views.test.fault),
    url(r'^ws/test/allgroup/$', views.test.allgroup),

    # emergency项目 Websocket测试API
    url(r'^ws/test/kafka/$', views.test.kafka),
    url(r'^ws/test/kafka_seek/$', views.test.kafka_seek),
    url('^api/telephone/$', views.EmployTelephone.as_view()),
    url('^api/SystemManager/$', views.SystemManager.as_view()),
    url('^api/export/$', views.ExportExcel.as_view()),


]


