"""
Desc: 企业微信消息类型模板插件
"""
from apps.emergency import models


class BaseWecomMsg(object):
    """通知msg基类"""

    def __init__(self, group, *args):
        self.group = group
        self.title = "[事件] - %s" % (self.group._meta.verbose_name)
        self.EmergencyOmnibus_level = dict(
            models.choices.get('EmergencyOmnibus_level'))
        if group.event_id:
            self.event = models.Event.objects.get(pk=self.group.event_id)
            self.Event_level = dict(models.choices.get('Event_level'))

    def msg():
        raise NotImplementedError('%s中必须实现msg方法' % self.__class__.__name__)


class Text(BaseWecomMsg):
    """告警text类型的Wecom msg 
    """

    def __init__(self, *args):
        super(Text, self).__init__(*args)
        self.url = '/#/'
        if self.group.event_id:
            self.url = '/#/emergency/' + \
                self.event._meta.model_name + '/' + str(self.event.pk)

    def msg(self):
        if isinstance(self.group, models.EmergencyOmnibusGroup):
            msg = {
                "content": '''%s\n时　间: %s\n级　别: %s\n系　统: %s\n描　述: %s''' % (
                    self.title,
                    self.group.storage_datetime,
                    self.EmergencyOmnibus_level.get(self.group.level),
                    self.group.system_cn,
                    self.group.summary,
                )
            }
        if isinstance(self.group, models.EmergencyOvertimeGroup):
            msg = {
                'content': '''%s\n时　间: %s-%s\n笔  数: %s\n渠  道: %s\n交易码: %s''' % (
                    self.title,
                    self.group.start_time,
                    self.group.end_time,
                    self.group.error_count,
                    # self.group.system_cn,
                    self.group.qudao_cn,
                    self.group.code,
                )
            }
        if hasattr(self, 'event'):
            msg['content'] += '''\n------------------\n事　件: %s\n级　别: %s\n单　号: %s\n\n[点击处理本次事件](%s)''' % (
                '已关联' if self.event else '未关联',
                self.Event_level.get(self.event.level),
                self.event.number,
                self.url,
            )
        return msg


class MarkDown(BaseWecomMsg):
    """告警markdown类型的Wecom msg 
    """

    def __init__(self, *args):
        super(MarkDown, self).__init__(*args)
        self.url = '/#/'
        if self.group.event_id:
            self.url = '/#/emergency/' + \
                self.event._meta.model_name + '/' + str(self.event.pk)

    def msg(self):
        if isinstance(self.group, models.EmergencyOmnibusGroup):
            msg = {
                'content': '''**%s**
                    >时　间: <font color=\"comment\">%s</font>
                    >级　别: <font color=\"info\">%s</font>
                    >系　统: <font color=\"info\">%s</font>
                    >描　述: <font color=\"comment\">%s</font>
                    ''' % (
                    self.title,
                    self.group.storage_datetime,
                    self.EmergencyOmnibus_level.get(self.group.level),
                    self.group.system_cn,
                    self.group.summary,)
            }
        if isinstance(self.group, models.EmergencyOvertimeGroup):
            msg = {
                'content': '''
                    >时　间: <font color=\"comment\">%s-%s</font>
                    >笔  数: <font color=\"info\">%s</font>
                    >系  统: <font color=\"info\">%s</font>
                    >渠  道: <font color=\"comment\">%s</font>
                    >交易码: <font color=\"comment\">%s</font>
                    >。
                    ''' % (
                    self.group.start_time,
                    self.group.end_time,
                    self.group.error_count,
                    self.group.system_cn,
                    self.group.qudao_cn,
                    self.group.code,
                )
            }
        if hasattr(self, 'event'):
            msg['content'] += '''><font color=\"blue\">------------------</font> 
                >事　件: `%s`
                >级　别: `%s`
                >单　号: `%s`
                >
                >[点击处理本次事件](%s)
                ''' % (
                '已关联' if self.event else '未关联',
                self.Event_level.get(self.event.level),
                self.event.number,
                self.url,
            )
        return msg


class TextCard(BaseWecomMsg):
    """综合类告警textcard类型的Wecom msg 
    """

    def __init__(self, *args):
        super(TextCard, self).__init__(*args)
        self.url = '/#/'
        self.btntxt = '无事件'
        if self.group.event_id:
            self.url = '/#/emergency/' + \
                self.event._meta.model_name + '/' + str(self.event.pk)
            self.btntxt = '点击处理'
            self.msg_description_extent = '''<div class=\"blue\">------------------</div><div class=\"blue\">事　件: %s</div><div class=\"blue\">级　别: %s</div><div class=\"blue\">单　号: %s</div>''' % (
                '已关联' if self.event else '未关联',
                self.Event_level.get(self.event.level),
                self.event.number,
            )

    def msg(self):
        if isinstance(self.group, models.EmergencyOmnibusGroup):
            msg = {
                "title": self.title,
                "description": '''<div class=\"blue\">时 间: %s</div><div class=\"red\">级 别: %s</div><div class=\"green\">系 统: %s</div><div class=\"gray\">描 述: %s</div>''' % (
                    self.group.storage_datetime,
                    self.EmergencyOmnibus_level.get(self.group.level),
                    self.group.system_cn,
                    self.group.summary,
                ),
                "url": self.url,
                "btntxt": self.btntxt
            }
        if isinstance(self.group, models.EmergencyOvertimeGroup):
            msg = {
                "title": "%s" % self.title,
                "description": '''<div class=\"blue\">时 间: %s-%s</div><div class=\"red\">笔 数: %s</div><div class=\"green\">系 统: %s</div><div class=\"gray\">渠 道: %s</div><div class=\"gray\">交易码: %s</div>''' % (
                    self.group.start_time,
                    self.group.end_time,
                    self.group.error_count,
                    self.group.system_cn,
                    self.group.qudao_cn,
                    self.group.code,
                ),
                "url": self.url,
                "btntxt": self.btntxt
            }
        if hasattr(self, 'event'):
            msg['description'] += self.msg_description_extent
        return msg
