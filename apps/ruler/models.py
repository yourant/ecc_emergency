from django.db import models

from jsonfield import JSONField


# Create your models here.


class Rule(models.Model):
    """规则"""
    is_enable = models.BooleanField(verbose_name='是否启用', default=False)
    title = models.CharField(max_length=128, verbose_name='规则名称', null=True)
    describe = models.TextField(verbose_name='规则描述', null=True)
    datetime_create = models.DateTimeField(
        '创建时间', auto_now_add=True, null=True, help_text='自动创建,无需人工填写')
    # 使用save可以达到自动更新的效果，使用update不会自动更新，因此需要携带上这个字段
    datetime_modify = models.DateTimeField(
        '更新时间', auto_now=True, null=True, help_text='自动创建,无需人工填写')
    rule = JSONField(verbose_name='规则(JSON格式)')

    class Meta:
        verbose_name = '规则'
        abstract = True


class EmergencyOmnibusRule(Rule):
    """告警聚合规则表"""

    class Meta:
        verbose_name = '综合类告警聚合规则'


class EmergencyOvertimeRule(Rule):
    """告警聚合规则表"""

    class Meta:
        verbose_name = '交易类告警聚合规则'