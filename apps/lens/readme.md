# lens —— Django组件
- 通用增删改查API:
    - 'GET', 'POST', 'PATCH', 'DELETE' 对应:查增改删。
- 自定义表字段显示控制。
- 全表字段模糊搜索。
- 指定表字段精确匹配搜索。
- 查询指定表字段最大、最小值。
- 分页控制。
- 自定义以指定字段进行排序。

## Config
1. 将整个组件作为app拷贝进已有django项目中。
2. 注册: `settings.INSTALLED_APPS`中添加`lens.apps.LensConfig`。
3. 配置: 在需要使用lens插件的app内新建lens.py文件，对model进行配置，示例如下:

example:
    
    # 1. 引入lens、lens封装的model配置类、需要使用lens的models
    from apps.lens import lens, ModelConfig
    from apps.emergency import models

    # 2. 配置model
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

        def hook_get_after(self, request, pk=None):
            '''钩子函数: 在成功查询一条或多条数据后需要执行的逻辑
            '''
            pass

        def hook_post_after(self, request):
            '''钩子函数: 在成功增加一条数据后需要执行的逻辑
            '''
            print('hook_post_after', '例如成功增加一条事件数据后 可以在这里执行向企业微信推送消息的逻辑',)

            pass

        def hook_patch_after(self, request, pk=None):
            '''钩子函数: 在成功更新一条数据后需要执行的逻辑
            '''
            print('hook_patch_after', '例如在成功更新一条事件处理状态后 可以在这里执行实时推送到websocket的逻辑')
            pass


        def hook_delete_after(self, request, pk=None):
            '''钩子函数: 在成功删除一条数据后需要执行的逻辑
            '''
            print('hook_delete_after', '例如在成功删除一条事件后 可以在这里执行实时推送到相关的逻辑')
            pass

    # 3. 将需要使用lens的model及写好的对应配置类注册到lens插件 即可完成配置
    lens.register(models.Event, Event)


## Usage
### 直接访问lens通用API即可
'GET', 'POST', 'PATCH', 'DELETE' 对应:查增改删

### 后端项目内调用lens通用API
可用django内置的HttpRequest跳过http请求这一步 直接访问lens的API以提高效率 调用示例如下:

example:

    # 1 获取lens插件中的model对象
    model_obj = lens._registry.get(models.EmergencyOmnibusGroup)

    # 2 发送请求
    response = model_obj._api('get', data)
    print('response即为API返回的数据', response)

    # 'GET', 'POST', 'PATCH', 'DELETE' 对应:查增改删

    # GET: 定义查询条件 data为空则返回全表所有数据（分页方式）
    # data = {
        # 'pk': 1,    # 获取指定主键的那条数据
        # 'q': 1, # 模糊搜索全表字段 或search_list中规定的字段范围
        # 'max': 'id', # 返回指定字段的最大值的那条数据
        # 'min': 'id', # 返回指定字段的最小值的那条数据
        # '当前model的任意字段名': '任意值', # 返回匹配任意字段名与任意值的那条数据
    # }

    # POST: 在data中以dict定义每个字段的值 因为是增加数据因此不支持定义pk
    data = {
        'level': 0, # 前端传入的事件级别
        'number': '233', # 前端传入的事件单号
    }

    # PATCH: data中以dict定义要修改字段的值
    # DELETE: data中以dict定义pk 不可定义其它字段