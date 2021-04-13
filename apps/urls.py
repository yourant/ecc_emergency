from django.conf.urls import include, url

# from apps.emergency import urls
from apps import lens
print('lens.views.schema.ModelSchema', dir(lens.views.schema.ModelSchema))
from apps.emergency import views

urlpatterns = [
    # lens插件封装的所有表的增删改查入口(restful API)
    url(r'^v1/', lens.lens.urls),
    # url(r"^v2/schema/(?P<app_name>\w+)/(?P<model_name>\w+)/",
    # views.schema.ModelSchema.as_view(), name='app_model'),
    url(r'^v2/schema/(?P<app_name>\w+)/(?P<model_name>\w+)/',
        lens.views.schema.ModelSchema.as_view(), name='app_model'),

    # url(r"^v2/test/formio/$", views.test.formio)

    # 除通用增删改查外 本项目额外需要的API可以在这里增加
    # url(r'^emergency', include('apps.emergency.urls')),
    url(r'^data/', include('apps.emergency.kafkadata.urls')),

]
