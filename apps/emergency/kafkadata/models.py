from django.db import models

# Create your models here.


class OffsetModel(models.Model):
    topic = models.CharField(max_length=128, verbose_name='主题')
    partition = models.IntegerField(verbose_name='分区')
    offset = models.IntegerField(verbose_name='偏移量')

    class Meta:
        abstract = True
        verbose_name = '记录抽象表'


class FailedOffset(OffsetModel):
    is_success = models.BooleanField(default=False, verbose_name='是否成功写入')
    time_into_db = models.DateTimeField(auto_now=True, verbose_name='入库时间')


class FaultLocation(OffsetModel):
    value = models.TextField(verbose_name='内容', null=True, blank=True)
    time_into_db = models.DateTimeField(auto_now=True, verbose_name='入库时间')
