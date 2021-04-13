import json
from django.db import models
import django.db.models.options as options

# 自定义Meta新属性
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('field_map',)

# Create your models here.


choices = {
    'Event_level': (
        (0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')
    ),
    'EmergencyGroup_status': (
        (0, '未处理'), (1, '已通知 待处理'), (2, '已处理')
    ),
    'EmergencyOmnibus_opration': (
        (0, '应用'), (1, '中间件'), (2, '数据库'), (3, '操作系统'), (4, '其他')
    ),
    'EmergencyOmnibus_level': (
        (10, '提示'), (20, '关注'), (40, '严重'), (50, '高危'), (0, '其他')
    ),
    # 'EmergencyOvertime_status': (
    #     (0, '未确认'), (1, '已确认')
    # )
}


# 事件 -----------


class Event(models.Model):
    '''事件表'''
    level = models.SmallIntegerField(
        verbose_name='事件级别', choices=choices.get('Event_level'), blank=True, null=True)
    number = models.CharField(
        verbose_name='事件单号', max_length=128, blank=True, null=True)
    dealer = models.CharField(verbose_name='处理人', max_length=128, blank=True)
    remark = models.TextField(verbose_name='处理建议', blank=True)

    def __str__(self):
        return '事件ID:%s,级别:%s,单号:%s' % (self.id, self.level, self.number)

    class Meta:
        verbose_name = '事件'


# 告警聚合 -----------


class EmergencyGroup(models.Model):
    '''告警聚合抽象表'''
    event = models.OneToOneField(
        verbose_name='所属事件', to=Event, to_field='id', on_delete=models.CASCADE, blank=True, null=True)
    status = models.SmallIntegerField(
        verbose_name='告警状态', choices=choices.get('EmergencyGroup_status'), default=0)
    storage_datetime = models.DateTimeField(
        verbose_name='入库时间', blank=True, null=True)
    system_cn = models.CharField(
        verbose_name='告警系统/来源', max_length=128, blank=True, null=True,
        help_text='根据system去cmdb中查询')

    # def toJSON(self):
    #     return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

    class Meta:
        verbose_name = '告警聚合抽象表'
        abstract = True


class EmergencyOmnibusGroup(EmergencyGroup):
    '''综合类告警聚合表'''
    occurrence_time = models.TimeField(
        verbose_name='告警时间', blank=True, null=True)
    summary = models.TextField(
        verbose_name='告警描述', blank=True)
    contact = models.TextField(
        verbose_name='联系人', blank=True)
    level = models.SmallIntegerField(
        verbose_name='告警分级', choices=choices.get('EmergencyOmnibus_level'), default=10, blank=True)

    # def save(self,*args,**kwargs):
    #     print('save *args,**kwargs', self, *args,**kwargs)
    #     old = EmergencyOmnibusGroup.objects.filter(pk=self.pk).first()
    #     if old:
    #         if old.status!=self.status:
    #             print('save status changed')
    #     super(EmergencyOmnibusGroup, self).save(*args,**kwargs)

    # def clean_status(self):
    #     # when field is cleaned, we always return the existing model field.
    #     print('clean_status', self.cleaned_data.get('status'))
    #     return 'self.instance.status'

    class Meta:
        verbose_name = '综合类告警聚合'


class EmergencyOvertimeGroup(EmergencyGroup):
    '''交易类告警聚合表'''

    start_time = models.TimeField(verbose_name='开始时间', blank=True, null=True)
    end_time = models.TimeField(verbose_name='最后时间', blank=True, null=True)
    error_count = models.IntegerField(
        verbose_name='超时数量(笔数)', blank=True, null=True)
    key = models.CharField(verbose_name='唯一标识',
                           max_length=128, blank=True, null=True)
    # 需进一步查询联系人是谁
    # contact = models.TextField(
    #     verbose_name='联系人', blank=True)
    # 需要去cmdb中查询
    # system_cn = models.CharField(
    #     verbose_name='告警系统/来源(中文 根据system去cmdb中查询)', max_length=128, blank=True)
    qudao_cn = models.CharField(
        verbose_name='渠道翻译', max_length=256, blank=True, null=True)
    server_cn = models.CharField(
        verbose_name='服务码翻译', max_length=256, blank=True, null=True)
    branch_cn = models.CharField(
        verbose_name='机构码翻译', max_length=256, blank=True, null=True)
    code = models.CharField(
        verbose_name='交易码', max_length=128, blank=True, null=True)
    code_cn = models.CharField(
        verbose_name='交易码翻译', max_length=256, blank=True, null=True)
    rtcode_cn = models.CharField(
        verbose_name='返回码翻译', max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = '交易类告警聚合'


# 告警 -----------


class Emergency(models.Model):
    '''告警抽象表'''
    is_checkbox = models.BooleanField(default=False)
    hash_id = models.CharField(max_length=32, verbose_name='哈希值', null=True)

    # 比原始数据新增的field:
    # hash_id
    class Meta:
        verbose_name = '告警抽象表'
        abstract = True


class EmergencyOmnibus(Emergency):
    '''综合类告警'''
    group = models.ForeignKey(
        verbose_name='综合类告警聚合ID', to=EmergencyOmnibusGroup, to_field='id', on_delete=models.CASCADE, blank=True, null=True)
    occurrence_time = models.TimeField(
        verbose_name='告警时间', blank=True, null=True)
    storage_timestamp = models.CharField(
        verbose_name='入库时间戳', max_length=18, null=True, blank=True)
    summary = models.CharField(
        verbose_name='告警描述', max_length=255, null=True, blank=True)
    mastertid = models.CharField(
        verbose_name='告警事件的告警组', max_length=128, null=True, blank=True)
    contact = models.TextField(
        verbose_name='联系人', null=True, blank=True)
    is_import = models.NullBooleanField(verbose_name='影响是否重要')
    operation = models.SmallIntegerField(
        verbose_name='事件类型', choices=choices.get('EmergencyOmnibus_opration'), blank=True)
    swapiden = models.CharField(
        verbose_name='告警类型', max_length=128, null=True, blank=True)
    tally = models.IntegerField(verbose_name='告警次数', null=True, blank=True)
    ntlogged = models.CharField(
        verbose_name='', max_length=256, null=True, blank=True)
    dep = models.IntegerField(
        verbose_name='告警机构(9999是总行)', null=True, blank=True)
    first_occurrence = models.CharField(
        verbose_name='第一次告警时间戳', max_length=18, blank=True, null=True)
    last_occurrence = models.CharField(
        verbose_name='最后一次告警时间戳', max_length=18, blank=True, null=True)
    severity = models.IntegerField(
        verbose_name='告警级别', null=True, blank=True)
    server_name = models.CharField(
        verbose_name='告警来源', max_length=128, null=True, blank=True)
    bapp_system = models.CharField(
        verbose_name='告警机器所属系统', max_length=128, null=True, blank=True)
    level = models.SmallIntegerField(
        verbose_name='告警分级', choices=choices.get('EmergencyOmnibus_level'), default=10, blank=True)
    operator = models.CharField(
        verbose_name='', max_length=128, null=True, blank=True)
    jyresult = models.CharField(
        verbose_name='', max_length=128, null=True, blank=True)
    node = models.GenericIPAddressField(
        verbose_name='告警机器IP', null=True)
    confirm_msg = models.TextField(
        verbose_name='告警事件处理信息', max_length=255, null=True, blank=True)
    system = models.CharField(
        verbose_name='告警系统(来源)', max_length=128, null=True, blank=True)
    # 需要去cmdb中查询
    system_cn = models.CharField(
        verbose_name='告警系统(来源)翻译', max_length=128, null=True, blank=True)
    acknowledged = models.CharField(
        verbose_name='', max_length=128, null=True, blank=True)
    identifier = models.CharField(
        verbose_name='', max_length=128, null=True, blank=True)

    # 比原始数据新增的field:
    # group
    class Meta:
        verbose_name = '综合类告警'
        field_map = {
            'ttime': 'occurrence_time',
            'isCheckbox': 'is_checkbox',
            'isImport': 'is_import',
            'firstoccurrence': 'first_occurrence',
            'lastoccurrence': 'last_occurrence',
            'servername': 'server_name',
            'statechange': 'storage_timestamp',
            'systemcn': 'system',
            'system': 'system_cn',
            'confirmMsg': 'confirm_msg',
            'url': 'level',
        }


class EmergencyOvertime(Emergency):
    '''交易类告警'''
    group = models.ForeignKey(
        verbose_name='交易类告警聚合ID', to=EmergencyOvertimeGroup, to_field='id', on_delete=models.CASCADE, blank=True, null=True)
    storage_timestamp = models.CharField(
        verbose_name='入库时间戳', max_length=18, null=True, blank=True)
    start_time = models.TimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.TimeField(verbose_name='最后时间', null=True, blank=True)
    error_count = models.IntegerField(verbose_name='超时数量(笔数)', null=True)
    system = models.CharField(verbose_name='告警渠道(来源)',
                              max_length=256, null=True, blank=True)
    # 需要去cmdb中查询
    system_cn = models.CharField(
        verbose_name='告警系统(来源)翻译', max_length=128, null=True, blank=True)
    qudao = models.CharField(
        verbose_name='渠道', max_length=128, null=True, blank=True)
    qudao_cn = models.CharField(
        verbose_name='渠道翻译', max_length=256, null=True, blank=True)
    server = models.CharField(
        verbose_name='服务码', max_length=128, null=True, blank=True)
    server_cn = models.CharField(
        verbose_name='服务码翻译', max_length=256, null=True, blank=True)
    branch_cn = models.CharField(
        verbose_name='机构码翻译', max_length=256, null=True, blank=True)
    code = models.CharField(
        verbose_name='交易码', max_length=128, null=True, blank=True)
    code_cn = models.CharField(
        verbose_name='交易码翻译', max_length=128, null=True, blank=True)
    rtcode = models.CharField(
        verbose_name='返回码', max_length=128, null=True, blank=True)
    rtcode_cn = models.CharField(
        verbose_name='返回码翻译', max_length=256, null=True, blank=True)
    key = models.CharField(verbose_name='唯一标识', max_length=128)
    route = models.CharField(
        verbose_name='路由', max_length=256, null=True, blank=True)

    # 数据源中无此字段 文档中有此字段
    # status = models.SmallIntegerField(
    #     verbose_name='状态', choices=choices.get('EmergencyOvertime_status'), default=0)

    # 比原始数据新增的field:
    # code_cn, group
    class Meta:
        verbose_name = '交易类告警'
        field_map = {
            'timestamp': 'storage_timestamp',
            'isCheckbox': 'is_checkbox',
            'system': 'system_cn',
            'qudaocn': 'qudao_cn',
        }


# 人员及系统 -----------


class Employee(models.Model):
    '''ITIL人员信息'''
    StaffName = models.CharField(
        verbose_name='姓名', max_length=32, null=True, blank=True)
    OrgName = models.CharField(
        verbose_name='部门', max_length=128, null=True, blank=True)
    Company = models.CharField(
        verbose_name='公司', max_length=128, null=True, blank=True)
    Mobile = models.CharField(
        verbose_name='手机号', max_length=16, null=True, blank=True)
    Account = models.CharField(
        verbose_name='账号', max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = 'ITIL人员信息'


ImportantSystem = ['个人网银系统', '企业网银系统', 'Call Center系统', '手机银行系统', '华夏E商宝系统',
                   '短信系统', '柜面系统', '自助设备前置系统', '网站门户系统', '外汇清算系统', 'SWIFT系统', '集中银联前置系统',
                   '核心系统', '借记卡系统', '金融IC卡系统', '国际结算系统', '票据综合管理系统', '同城票据交换系统',
                   '信贷管理系统', '理财系统', '国债系统', '基金代销系统', '黄金买卖系统', '第三方存管系统', '支付融资系统',
                   '资产托管系统', '外汇牌价系统', '支付密码系统', '指纹授权系统', 'RA系统', '综合前置系统', 'BEAI系统',
                   '第二代支付系统', '直销银行系统', '信用卡互联与清算系统', '资金存管系统', '网联接入系统', '银联无卡支付系统', '骨干网络系统',
                   ]


class System(models.Model):
    name = models.CharField(verbose_name='系统名称',
                            max_length=32, null=True, blank=True)
    managers = models.ManyToManyField(Employee, blank=True)

    def manager_list(self):
        return ','.join([i.Account for i in self.Employee.all()])
