from django import forms

from apps.emergency.kafkadata.models import OffsetModel
from apps.lens import lens, ModelConfig
from apps.emergency import models


class Event(ModelConfig):
    """事件数据表配置 其它表均可根据此来进行灵活配置"""

    # 允许显示的字段
    list_display = []
    # 禁止显示的字段
    list_block = ['emergencyomnibusgroup', 'emergencyovertimegroup']
    # 模糊搜索的字段范围
    search_list = []
    # 指定以某些字段排序
    order_by = []
    # action_list = ['multi_delete']
    is_pagination = False


class EmergencyGroupModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmergencyGroupModelForm, self).__init__(*args, **kwargs)

    def clean_event(self):
        # when field is cleaned, we always return the existing model field.
        # 若无则添加 若有则保持原数据禁止修改
        if self.instance.event:
            return self.instance.event
        return self.cleaned_data.get('event')


class EmergencyOmnibusGroup(ModelConfig):
    """综合类告警聚合数据表配置"""
    # list_block = ['storage_datetime']
    # search_list = ['emergencyomnibus', 'event']
    order_by = ['-storage_datetime', '-occurrence_time']
    model_form_class = EmergencyGroupModelForm
    is_pagination = False
    depth = 1


class EmergencyOvertimeGroup(ModelConfig):
    """综合类告警聚合数据表配置"""
    list_block = ['storage_datetime']
    order_by = ['-start_time']
    is_pagination = False
    depth = 1


class EmergencyOmnibus(ModelConfig):
    """综合类告警数据表配置"""
    is_pagination = False


class EmergencyOvertime(ModelConfig):
    """交易类告警数据表配置"""
    list_display = []
    list_block = []
    order_by = []
    is_pagination = False


class Employee(ModelConfig):
    """交易类告警数据表配置"""
    list_display = []
    list_block = []
    order_by = []
    is_pagination = False


# 将每个model及对应配置注册到lens插件
lens.register(models.Event, Event)
lens.register(models.EmergencyOmnibusGroup, EmergencyOmnibusGroup)
lens.register(models.EmergencyOvertimeGroup, EmergencyOvertimeGroup)
lens.register(models.EmergencyOmnibus, EmergencyOmnibus)
lens.register(models.EmergencyOvertime, EmergencyOvertime)
lens.register(models.Employee, Employee)
lens.register(OffsetModel)
