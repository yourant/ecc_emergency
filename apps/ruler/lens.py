from apps.lens import lens, ModelConfig
from apps.ruler import models


class EmergencyOmnibusRule(ModelConfig):
    """lens数据表配置"""

    # 允许显示的字段
    list_display = []
    # 禁止显示的字段
    list_block = []
    # 模糊搜索的字段范围
    search_list = []
    # 指定以某些字段排序
    order_by = []
    # action_list = ['multi_delete']


class EmergencyOvertimeRule(ModelConfig):
    """lens数据表配置"""

    # 允许显示的字段
    list_display = []
    # 禁止显示的字段
    list_block = []
    # 模糊搜索的字段范围
    search_list = []
    # 指定以某些字段排序
    order_by = []
    # action_list = ['multi_delete']


# 将每个model及对应配置注册到lens插件
lens.register(models.EmergencyOmnibusRule, EmergencyOmnibusRule)
lens.register(models.EmergencyOvertimeRule, EmergencyOvertimeRule)

# 配置完lens插件
# 接下来就可以通过restful API风格的http的请求 对model进行增删改查 以及提供的其它高级查询功能了

# 项目内调用可用django内置的HttpRequest跳过http请求这一步 直接访问lens的API以提高效率
# 调用示例参考lens.readme.md
