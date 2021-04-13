import functools
import json
import re
# from types import FunctionType

from django.conf.urls import url
# from django.utils.safestring import mark_safe
# from django.shortcuts import HttpResponse, render, redirect
from django.http import QueryDict, JsonResponse
from django.http.request import HttpRequest
# from django.http import FileResponse
# from django.urls import reverse
from django import forms
from django.db.models import Q, Avg, Max, Min, Count, Field
from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.db.models.fields.reverse_related import ForeignObjectRel, ManyToManyRel, ManyToOneRel, OneToOneRel
from django.core import serializers
from django.forms.models import model_to_dict

from apps.lens import utils
from apps.lens.utils import logger

# from rest_framework.decorators import api_view
# from rest_framework.views import APIView

# 生产环境请将config.dev中的DEBUG设置为False 部分不安全的接口与测试功能将关闭
from config.dev import DEBUG


# 根据DEBUG切换开发/生产环境下被允许的请求方法
if DEBUG:
    ACCEPT_REQUEST_METHOD = [
        'GET', 'POST', 
        'PATCH', 'DELETE'
    ]
else:
    ACCEPT_REQUEST_METHOD = ['GET', 'POST', 'PATCH', ]

# 允许的聚合查询
ACCEPT_AGGREGATE = {
    # 'avg': Avg, 
    'max': Max, 
    'min': Min, 
    # 'count': Count
}

# class ModelAPI(APIView):
#     """docstring for ModelAPI"""
#     # def __new__(cls, model_config=None):
        
#     #     instance = super().__new__(cls)
#     #     instance.model_config = model_config

#     #     #3.返回对象的引用
#     #     return instance

#     def __init__(self, model_config=None):
#         super(ModelAPI, self).__init__()
#         self.model_config = model_config
#         print('self.model_config', self, model_config, self.model_config)

#     def get(self, request, *args, **kwargs):
#         print('get request', self, dir(self), self.request._request, dir(self.request._request), self.model_config, *args, **kwargs)
#         md = self.model_config.get_model_data(request, pagination=True)

#         response = utils.ApiResponse(code=1, data=md.data)
#         print('response.__dict__', md.data, response.__dict__)
#         return JsonResponse(
#             response.__dict__,
#         #     safe=False, # 如果待序列化对象不是dict
#         #     # charset='utf-8',
#             json_dumps_params={'ensure_ascii': False},
#             )
    
#     def delete(self, request):
#         request.DELETE = QueryDict(request.body)
#         print('data DELETE', 
#             # request.body, 
#             request.data,
#         request.DELETE, dir(request))
#         action_name = request.DELETE.get('action')
#         action_dict = [{'name': func.__name__, 'text': func.text} for func in self.get_action_list()]
#         print('action_name action_dict', action_name, action_dict)
#         if not action_name:
#             msg = '请求中没有指定批量操作方法'
#         elif action_name not in action_dict:
#             # return HttpResponse('非法请求')
#             msg = '不存在%s方法' % action_name
#         else:
#             # 请求中若有合法action
#             response = getattr(self, action_name)(request)
#             print('data response',response)
#             return JsonResponse(
#                 response.__dict__,
#                 json_dumps_params={'ensure_ascii': False},
#                 )

#         return JsonResponse(
#             utils.ApiResponse(code=-1, msg=msg).__dict__,
#             json_dumps_params={'ensure_ascii': False},
#             )

#     def post(self, request):
#         AddModelForm = self.get_model_form_class()
#         form = AddModelForm(request.POST)
#         print('form', form.errors.as_json(), type(form.errors.as_json()))
#         code = -1

#         if form.is_valid():
#             form.save()
#             code = 1

#         data = json.loads(form.errors.as_json())
#         response = utils.ApiResponse(code, data=data)
#         return JsonResponse(
#             response.__dict__,
#             json_dumps_params={'ensure_ascii': False},
#             )
        


class ModelData(object):
    """非前后端分离模式下 model的数据序列化类
    """

    def __init__(self, config, queryset, q, search_list, page=None, count=None, pagination=True):
        '''
        Arguments:
            config {[ModelConfig]} -- [model的配置类]
            queryset {[type]} -- [description]
            q {[type]} -- [description]
            search_list {[type]} -- [description]
        
        Keyword Arguments:
            page {[type]} -- [description] (default: {None})
            count {[type]} -- [description] (default: {None})
            pagination {bool} -- [是否分页 若否 某些值就无须构建] (default: {True})
        '''
        # logger.info('ModelData __init__',
        #     config
        # )

        self.q = q
        self.search_list = search_list
        self.page = page
        self.count = count
        self.pagination = pagination

        self.config = config
        # self.action_list = [{'name': func.__name__, 'text': func.text} for func in config.get_action_list()]

        # if self.pagination:
        #     self.add_btn = config.get_add_btn()

        self.queryset = queryset

        self.list_display = config.get_list_display()
        self.list_filter = config.get_list_filter()


    # def gen_list_filter_rows(self):

    #     for option in self.list_filter:
    #         _field = self.config.model_class._meta.get_field(option.field)
    #         yield option.get_queryset(_field, self.config.model_class, self.config.request.GET)

    def get_rel_value(self, query, field):
        ''' 对model中的Rel字段进行取值
        
        [description]
        
        Arguments:
            filed {[string]} -- [field名称]
        
        Returns:
            [type] -- [description]
        '''
        # logger.info('get_rel_value',
        #     type(field),
        #     field,
        #     field.name,
        #     field.__dict__,
        #     queryset,
        #     queryset.__dict__
        #     type(query),
        #     query.__dict__,
        #     query.values_list(),
        #     )

        # 处理fk/m2m字段
        if isinstance(field, OneToOneRel):
            # logger.info('> OneToOneRel', 
            #     field.name,
            #     queryset.values_list('pk', flat=True),
            #     )
            queryset = getattr(query, field.name)
            # 根据配置类的depth决定是否进行反向关联字段的序列化
            if not self.config.depth:
                val = queryset.pk
            elif self.config.depth == 1:
                val = model_to_dict(queryset, fields=[field.name for field in queryset._meta.fields])
        elif isinstance(field, (ManyToOneRel, ManyToManyRel)):
            # logger.info('> ManyToOneRel, ManyToManyRel',
            #     )
            queryset = getattr(query, field.name + '_set').all()
            # 根据配置类的depth决定是否进行反向关联字段的序列化
            if not self.config.depth:
                val = [i.pk for i in queryset]
            elif self.config.depth == 1:
                val = list(queryset.values())

        # logger.info('> val',
        #     field.name,
        #     val,
        #     )
        return val

    def get_field_value(self, query, field):
        ''' 对model中的字段进行取值
        
        [description]
        
        Arguments:
            filed {[string]} -- [field名称]
        
        Returns:
            [type] -- [description]
        '''
        queryset = getattr(query, field.name)
        # logger.info('get_field_value',
        #     type(field),
        #     field,
        #     field.name,
        #     )

        # 处理fk、o2o/m2m字段(OneToOneField走的也是ForeignKey)
        if isinstance(field, ForeignKey):
            # logger.info('> ForeignKey',
            #     field,
            #     type(queryset),
            #     )
            if not queryset:
                val = None
            elif not self.config.depth:
                val = queryset.pk or queryset.__str__()
            elif self.config.depth == 1:
                # val = model_to_dict(queryset)
                val = model_to_dict(queryset, fields=[field.name for field in queryset._meta.fields])
        elif isinstance(field, (ManyToManyField,)):
            # logger.info('> ManyToManyField', 
            #     field.name,
            #     queryset.values_list('pk', flat=True),
            #     )
            queryset = getattr(query, field.name).all()
            if not self.config.depth:
                val = [i.pk for i in queryset]
            elif self.config.depth == 1:
                val = list(queryset.values())
        # 处理常规field
        else:
            # logger.info('> else',)
            val = queryset
        # logger.info('> val',
        #     field.name, val,
        #     )
        return val

    def get_item(self, query):
        ''' 获取一行的数据
        Arguments:
            query {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        '''
        item = {}
        # for field in self.list_display:
        # logger.info('get_fields_class',
        #     self.config.get_fields_class()
        #     )
        for field in self.config.get_fields_class():
            # logger.info('get_item field', type(field), field)
            if isinstance(field, (Field)):
                # 若为Model的常规字段 则进行取值
                # 若为ModelConfig.display_checkbox等非model字段 则跳过
                try:
                    val = self.get_field_value(query, field)
                except Exception as e:
                    # print('except:',e)
                    val = '无法处理的字段:%s, 错误:%s' % (field, str(e))
            elif isinstance(field, (ForeignObjectRel)):
                try:
                    val = self.get_rel_value(query, field)
                except Exception as e:
                    # print('except:',e)
                    val = '无法处理的Rel字段:%s, 错误:%s' % (field, str(e))
            else:
                continue
            item[field.name] = val
        return item

    def get_items(self):
        ''' 获取queryset中所有行的数据
        '''
        ts = []
        for query in self.queryset:
            print(query)
            ts.append(self.get_item(query))
        # return [self.get_item(query) for query in self.queryset]
        return ts

    @property
    def data(self):
        ''' 为API构造数据 对fk/m2m字段单独进行了处理
        '''
        _meta = self.config.model_class._meta
        # field = _meta.get_field('emergencyomnibus').related_model._meta.verbose_name
        # logger.info('data',
            # field,
            # dir(field),
            # _meta.__dict__,
            # str(self.config.model_class.__dict__),
            # )

        rows = {
            'app': {
                'name': _meta.app_label,
                'label': _meta.app_config.verbose_name,
            },
            'name': _meta.model_name,
            'table': _meta.model_name,
            'label': _meta.verbose_name,
            'fields': {
                _meta.get_field(k).name:(_meta.get_field(k).related_model._meta.verbose_name if isinstance(_meta.get_field(k), (ManyToManyRel, ManyToOneRel)) else _meta.get_field(k).verbose_name)
                for k in self.list_display
                if isinstance(k, str)
                },
            'items': self.get_items()
        }
        # logger.info('rows',
        #     rows,
        #     type(rows),
        #     dir(rows)
        #     )
            # yield row
        return rows


class ModelConfig(object):

    def multi_delete(self, request):
        """
        批量删除的action
        :param request:
        :return:
        """

        pk_list = request.data.get('pk_list', [])
        if len(pk_list) == 0:
            return JsonResponse(
                utils.ApiResponse(-1, '未选择任何项 指定参数(action)后 参数(pk_list)不能为空', {}).__dict__,
                json_dumps_params={'ensure_ascii': False},
            )
        if isinstance(pk_list, list):
            result = self.model_class.objects.filter(pk__in=pk_list).delete()
        else:
            result = self.model_class.objects.get(pk=pk_list).delete()
        # logger.info('multi_delete result', pk_list, result)
        data = {'result': list(result)}
        if result[0] == 0:
            code = -1
            msg = '数据库中无pk为%s的数据' % str(pk_list)
        else:
            code = 1
            msg = 'success'
        return JsonResponse(
            utils.ApiResponse(code, msg, data).__dict__,
            json_dumps_params={'ensure_ascii': False},
            )

    multi_delete.text = "批量删除"

    order_by = []
    list_display = []
    list_block = []
    model_form_class = None
    action_list = [multi_delete]
    search_list = []
    list_filter = []
    fields_class = []
    is_pagination = True
    depth = 0

    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site
        self.request = None
        self.back_condition_key = "_filter"
        self.page = 1
        self.per_page = 3

        # print('self.model_class._meta',self.model_class._meta.many_to_many)

    def get_order_by(self):
        return self.order_by

    def get_fields_class(self):
        ''' 获取model的字段类列表
        '''
        if self.fields_class:
            return self.fields_class

        self.fields_class = [field for field in self.model_class._meta.get_fields() if field.name not in self.list_block]
        return self.fields_class

    def get_fields_name(self):
        ''' 获取model的字段类名列表
        '''
        fields_name = [field.name for field in self.get_fields_class()]
        return fields_name

    def get_list_display(self):
        val = []
        # val.extend([ModelConfig.display_checkbox,ModelConfig.display_edit,ModelConfig.display_del,ModelConfig.display_index,])
        if self.list_display:
            if self.list_block:
                for x in self.list_block:
                    if x in self.list_display:
                        self.list_display.remove(x)
            val.extend(self.list_display)
        else:
            val.extend(self.get_fields_name())
        return val

    def get_action_list(self):
        val = []
        val.extend(self.action_list)
        return val

    def get_search_list(self):
        val = []
        if self.search_list:
            val.extend(self.search_list)
        else:
            val.extend(self.get_fields_name())
        return val

    def get_search_condition(self, request, pk=None):
        con = Q()
        search_list = self.get_search_list()  # ['name','tel']
        # q = request.GET.get('q', "")
        q = request.data.get('q', "")
        print(q, '889')
        if q:
            # 生成模糊搜索条件
            con.connector = "OR"
            for field in search_list:
                _field = self.model_class._meta.get_field(field)
                if isinstance(_field, (ManyToManyField, ManyToManyRel)):
                    continue
                elif isinstance(_field, (ForeignKey, ManyToOneRel)):
                    con.children.append(('%s__%s__contains' % (field, _field.target_field.name), q))
                else:
                    con.children.append(('%s__contains' % field, q))
        else:
            # 生成字段精确搜索条件
            con.connector = "AND"
            # 筛选出查询key 与 当前model的非外键fields的交集
            query_fields = set(request.data.keys())
            # print('5'*20, query_fields)
            query_fields = query_fields & {local_field.name for local_field in self.model_class._meta.local_fields}

            for field in query_fields:
                con.children.append(('%s' % field, request.data.get(field, "")))
            # print('query_fields', query_fields, search_list, q, con)

        return search_list, q, con

    def get_list_filter(self):
        val = []
        val.extend(self.list_filter)
        return val

    def get_list_filter_condition(self):
        comb_condition = {}
        for option in self.get_list_filter():
            element = self.request.GET.getlist(option.field)
            if element:
                comb_condition['%s__in' % option.field] = element

        return comb_condition


    def get_model_data(self, request, pk=None, pagination=True):
        '''[summary]
        
        [description]
        
        Arguments:
            request {[type]} -- [description]
        
        Keyword Arguments:
            pagination {bool} -- [是否分页] (default: {True})
        
        Returns:
            [type] -- [description]
        '''

        # ##### 处理搜索 #####
        search_list, q, con = self.get_search_condition(request, pk=pk)

        # 获取组合搜索筛选
        condition = self.get_list_filter_condition()
        # print('search_list, q, con', search_list, q, con, condition)
  
        # 生成Max、Min聚合查询条件并返回查询数据
        for key in ACCEPT_AGGREGATE.keys():
            # print('key, func', key)
            field = request.GET.get(key, '')
            if field:
                ret = self.model_class.objects.all().aggregate(value=ACCEPT_AGGREGATE.get(key)(field))
                # print('aggregate', ret, field)
                queryset = self.model_class.objects.filter(**{field:ret.get('value')})
                md = ModelData(self, queryset, q, search_list, pagination=pagination)
                return md

        # pagination若为False 则不处理分页及count
        if not pagination:
            queryset = self.model_class.objects.filter(con).filter(**condition).order_by(*self.get_order_by()).distinct()
            # print('queryset',queryset)

            # drf序列化
            # from apps.emergency import serializers
            # queryset = serializers.EmergencyOvertime(queryset, many=True)
            # print('queryset',queryset)

            md = ModelData(self, queryset, q, search_list, pagination=pagination)
        else:
            # ##### 处理分页 #####
            from apps.lens.utils import Pagination
            # print('con',type(con),con)
            total_count = self.model_class.objects.filter(con).count()
            query_params = request.GET.copy()
            query_params._mutable = True

            try:
                self.page = int(request.GET.get('page'))
            except Exception as e:
                self.page = 1

            page = Pagination(self.page, total_count, request.path_info, query_params, per_page=self.per_page)

            # 获取组合搜索筛选
            queryset = self.model_class.objects.filter(con).filter(**condition).order_by(*self.get_order_by()).distinct()[page.start:page.end]

            # 获取count
            count = self.model_class.objects.count()

            md = ModelData(self, queryset, q, search_list, page, count, pagination=pagination)

            # # 仅定制前端页面显示的字段
            # if 'id' in md.list_display:
            #     md.list_display.remove('id')

        return md.data

    def get_model_form_class(self):
        """
        获取ModelForm类
        :return:
        """
        # if self.model_form_class:
        #     return self.model_form_class

        if self.model_form_class:
            super_model_form_class = self.model_form_class
        else:
            super_model_form_class = forms.ModelForm

        class AddModelForm(super_model_form_class):
            class Meta:
                model = self.model_class
                fields = "__all__"
                # fields = ['facilityName']
                # labels = {"facilityName":"名字"}
                # error_messages ={
                #     "facilityName":{"required":"必填","invalid":"格式错误"}  ##自定义错误提示
                # }
        
            def __init__(self, *args, **kwargs):
                super(AddModelForm, self).__init__(*args, **kwargs)
                # name, field = list(self.fields.items())[0]
                # for x in dir(field):
                #     print('field[x]',name,type(field),dir(field))

                for name, field in self.fields.items():

                    # 对BooleanField、MultiSelectFormField做单独的样式处理
                    # from django.forms.fields import BooleanField
                    # from multiselectfield.forms.fields import MultiSelectFormField
                    # if not isinstance(field,(BooleanField,MultiSelectFormField)) :
                    #     field.widget.attrs['class'] = 'form-control form-control-sm'

                    field.widget.attrs['placeholder'] = field.help_text

        return AddModelForm


    def gen_request_data(self, request, pk):
        '''解析请求信息为dict并挂载到request.data
        
        [description]
        
        Arguments:
            request {[type]} -- [description]
            pk {int / string} -- 主键值
        
        Raises:
            Exception -- [description]
        '''
        if not DEBUG and request.method not in ACCEPT_REQUEST_METHOD:
            raise Exception('为保护数据安全 暂不允许%s请求方法' % request.method)

        # 若为项目内的非http请求
        if request.content_type in ['python/dict',]:
            if type(request.data) == dict and request.data.get('pk'):
                # 将pk值动态附加到主键值
                request.data[self.model_class._meta.pk.name] = request.data.get('pk')
        # 若为http请求
        else:
            if request.method == 'GET':
                request.data = dict(request.data, **QueryDict.dict(request.GET))
            else:
                body = json.loads(request.body)
                # 判断是否为允许的批量操作方法
                action_name = body.get('action')
                action_name_list = [func.__name__ for func in self.get_action_list()]
                # logger.info('action_name action_dict', action_name, action_name_list)
                if action_name:
                    if action_name not in action_name_list:
                        raise Exception('非法的操作方法(%s)' % action_name)

                    if not body.get('pk_list') and not isinstance(body.get('pk_list'), list):
                        raise Exception('指定操作方法的同时必须指定参数(pk_list) 且必须为一个list/array')

                elif request.method in ['PATCH', 'DELETE',] and not pk:
                    raise Exception('未指定操作方式的(%s)类型请求每次仅允许对单条数据进行操作 需在url中指定操作项主键值(通常为id)' % request.method)

                # 根据content_type解析请求数据为dict
                if request.content_type in ['application/json', 'text/plain']:
                    request.data = body
                
                elif request.content_type in ['multipart/form-data']:
                    # 转换form-data类型数据为dict
                    from django.http.multipartparser import MultiPartParser
                    query_dict, file = MultiPartParser(request.META, request, request.upload_handlers).parse()
                    request.data = QueryDict.dict(query_dict)

                else:
                    raise Exception('不支持的Content-Type: %s, 请确保使用此范围内的Content-Type: %s' % (request.content_type, str(['application/json', 'text/plain', 'multipart/form-data'])))

            if pk:
                # 将pk值动态附加到主键值
                request.data[self.model_class._meta.pk.name] = pk
                # logger.info('gen_request_data', request.data, body, pk)

        # if hasattr(request,'data'):
        #     print("if hasattr(request,'data')", type(request.data), request.data)

    def hook_get_after(self, request, pk=None):
        '''钩子函数: 在api成功查询一条或多条数据后执行
        '''
        pass

    def hook_post_before(self, request):
        '''钩子函数: 在api成功增加一条数据后执行
        '''
        pass

    def hook_post_after(self, request):
        '''钩子函数: 在api增加一条数据前执行
        '''
        pass

    def hook_patch_after(self, request, pk=None):
        '''钩子函数: 在api成功修改一条数据后执行
        '''
        pass

    def hook_delete_after(self, request, pk=None):
        '''钩子函数: 在api成功删除一条数据后执行
        '''
        pass

    # @api_view(['GET'])  # rest_framework装饰器
    def api(self, request, pk=None):
        """查询通用API(前后端分离版本)
        GET: 返回当前model所有数据, 若指定pk值则返回指定数据
        POST: 添加一条数据, 若request中含pk值则忽略pk值
        PATCH: 更新一条数据, 需指定pk值
        DELETE: 删除一条数据, 需指定pk值
        
        Arguments:
            request {[type]} -- [description]
            pk {int / string} -- 单条数据操作时所需要的主键值
        
        Returns:
            [type] -- [description]
        """
        if not hasattr(request, 'data'): request.data = {}
        code = -1
        msg = None
        data = {}
        # print(
        #     'request', 
        #     request.method,
        #     request.content_type,
        #     request.content_params,
        #     # request.body,
        #     request.data,
        #     )

            
        try:
            # 解析请求信息为dict并挂载到request.data
            self.gen_request_data(request, pk)
        except Exception as e:
            msg = '解析请求时发生异常 请参考data中的提示信息'
            data[e.__class__.__name__] = str(e)
            return JsonResponse(
                utils.ApiResponse(code, msg=msg, data=data).__dict__,
                json_dumps_params={'ensure_ascii': False},
                )


        if request.method == 'POST':
            # from django.db import transaction
            # with transaction.atomic():
            try:
                # 触发基于signals自定义的钩子
                utils.post_before.send(sender=self.model_class, request=request)
                # lens自定义钩子
                # self.hook_post_before(request)
                AddModelForm = self.get_model_form_class()
                form = AddModelForm(request.data)
                if form.is_valid():
                    # utils.valid_after.send(sender=self.model_class, request=request, old_instance=None, form=form)

                    instance = form.save(commit=False)
                    utils.valid_after.send(sender=self.model_class, request=request, instance=instance)
                    instance.save()

                    # Django不支持序列化单个model对象
                    # 因此用单个对象来构造一个只有一个对象的数组(类似QuerySet对象)
                    # 由于序列化QuerySet会被'[]'所包围
                    # 因此使用string[1:-1]来去除由于序列化QuerySet而带入的'[]'
                    data = json.loads(serializers.serialize('json',[instance])[1:-1])
                    code = 1
                    msg = 'success'
                    # self.hook_post_after(request)
                else:
                    data = json.loads(form.errors.as_json())
            except Exception as e:
                msg = '处理%s请求时发生异常 请参考data中的提示信息' % request.method
                data[e.__class__.__name__] = str(e)

        
        elif request.method in ['GET', 'PATCH', 'DELETE',]:
            if request.method == 'GET':
                try:
                    print(pk,self.is_pagination,'9090')
                    data = self.get_model_data(request, pk=pk, pagination=self.is_pagination)
                    code = 1
                    msg = 'success'
                    # self.hook_get_after(request, pk=pk)
                except Exception as e:
                    msg = '处理%s请求时发生异常 请参考data中的提示信息' % request.method
                    data[e.__class__.__name__] = str(e)
            else:
                if not pk:
                    # 若未指定pk就执行操作方法 request.data中是否包含action 已经在gen_request_data中进行了校验
                    action_name = request.data.get('action')
                    return getattr(self, action_name)(request)
                else:
                    # 指定了pk就进行常规单条数据的操作
                    # obj = self.model_class.objects.get(pk=pk)
                    obj = self.model_class.objects.filter(pk=pk).first()
                    if not obj:
                        msg = '数据表(%s)中无主键值为(%s)的项' % (self.model_class._meta.model_name, pk)
                    elif request.method == 'PATCH':
                        try:
                            utils.patch_before.send(sender=self.model_class, request=request, instance=obj)
                            # print('lens request', request.data)
                            # obj.update(**request.data)
                            # 针对单个对象 将update更换为__dict__.update + save 后可正常执行save钩子
                            # obj.__dict__.update(**request.data)
                            # obj.save()

                            AddModelForm = self.get_model_form_class()
                            for k,v in forms.models.model_to_dict(obj).items():
                                if k not in request.data: request.data[k] = v
                            form = AddModelForm(data=request.data, instance=obj)
                            if form.is_valid():
                                form.save(commit=False)
                                utils.valid_after.send(sender=self.model_class, request=request, instance=obj)
                                obj = form.save()
                                utils.patch_save.send(sender=self.model_class, request=request, instance=obj)

                                data = json.loads(serializers.serialize('json',[obj])[1:-1])
                                msg = '更新成功'
                                code = 1
                                # self.hook_patch_after(request, pk=pk)
                            else:
                                data = json.loads(form.errors.as_json())
                        except Exception as e:
                            msg = '处理(%s)请求时发生异常 请参考data中的提示信息' % request.method
                            data[e.__class__.__name__] = str(e)

                    elif request.method == 'DELETE':
                        logger.info('DELETE 2', request.data)
                        obj.delete()
                        msg = '删除成功'
                        code = 1
                        # self.hook_delete_after(request, pk=pk)

        # print('response.__dict__', data, response.__dict__)
        return JsonResponse(
            utils.ApiResponse(code, msg=msg, data=data).__dict__,
            json_dumps_params={'ensure_ascii': False},
            )

    def _api(self, method='GET', data={}):
        if not type(method) == str:
            raise Exception('关键词参数(method)类型请确保是String')
        else:
            method_upper = method.upper()
        if method_upper not in ACCEPT_REQUEST_METHOD:
            raise Exception('%s请求方法在当前环境下不被允许 前环境下被允许的method: %s' % (method, ACCEPT_REQUEST_METHOD))
        if not type(data) == dict:
            raise Exception('关键词参数(data)类型请确保是dict')

        # 直接调用lens内部封装的通用接口
        request = HttpRequest()
        # print('_api',
            # request.content_type,
            # request.body,
            # request.method,
            # request.data,
            # )
        request.content_type = 'python/dict'
        request.method = method_upper
        request.data = data
        response = self.api(request)
        return json.loads(response.content)


    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name

        urlpatterns = [
            url(r'^$', self.wrapper(self.api), name='%s_%s' % info),
            # url(r'^$', self.wrapper(self.api), name='%s_%s' % info),
        ]

        extra = self.extra_url()
        if extra:
            urlpatterns.extend(extra)

        return urlpatterns

    def extra_url(self):
        pass

    @property
    def urls(self):
        return self.get_urls()


class ModelAdmin(object):
    def __init__(self):
        self._registry = {}
        self.app_name = 'api'
        self.namespace = 'api'


    def register(self, model_class, lens_config=None):
        """将model和model的config类对应起来, 封装到admin对象（单例模式）中
        
        [description]
        
        Arguments:
            model_class {Model} -- 单个model表类
        
        Keyword Arguments:
            lens_config {ModelConfig} -- 与model表类对应的ModelConfig配置类 (default: {None})
        """
        if not lens_config:
            lens_config = ModelConfig
        self._registry[model_class] = lens_config(model_class, self)


    def app(self, request):
        '''返回当前lens中注册的所有app,model
        '''
        data = {}
        code = 0
        try:
            for k, v in self._registry.items():
                t = {
                    'name': k._meta.model_name,
                    'label': k._meta.verbose_name,
                }
                if not data.get(k._meta.app_label, []):
                    data[k._meta.app_label] = {
                        'name': k._meta.app_label,
                        'label': k._meta.app_config.verbose_name,
                        'info': k._meta.app_config.info,
                        'tables': {
                            k._meta.model_name: t
                        }
                    }
                else:
                    data[k._meta.app_label]['tables'][k._meta.model_name] = t

        except Exception as e:
            code = -1
            msg = 'fault'
        else:
            code = 1
        response = utils.ApiResponse(code, data=data)
        return JsonResponse(
            response.__dict__,
            json_dumps_params={'ensure_ascii': False},
            )


    def table(self, request):
        '''返回当前lens中注册的所有app,model
        '''
        data = {}
        code = 0
        try:
            table = []
            for k, v in self._registry.items():
                t = {
                    'app': k._meta.app_label,
                    'table': k._meta.model_name,
                    'label': k._meta.verbose_name,
                }
                table.append(t)
            data['table'] = table
        except Exception as e:
            code = -1
            msg = 'fault'
        else:
            code = 1
        response = utils.ApiResponse(code, data=data)
        return JsonResponse(
            response.__dict__,
            json_dumps_params={'ensure_ascii': False},
            )

    def get_urls(self):

        urlpatterns = []
        urlpatterns.append(url(r'^app/$', self.app))
        urlpatterns.append(url(r'^table/$', self.table))

        for k, v in self._registry.items():
            app_label = k._meta.app_label
            model_name = k._meta.model_name
            urlpatterns.append(url(r'^%s/%s/' % (app_label, model_name,), (v.urls, None, None)))
            urlpatterns.append(url(r'^%s/%s/(?P<pk>\d+)' % (app_label, model_name,), (v.urls, None, None)))

        extra = self.extra_url(self)
        if extra:
            urlpatterns.extend(extra)

        return urlpatterns


    def extra_url(self, *args, **kwargs):
        # print('args kwargs', args,kwargs)
        pass


    @property
    def urls(self):
        urls = self.get_urls(), self.app_name, self.namespace
        return urls

    # @property
    # def api(self):
    #     urls = self.get_api(), 'apis', 'apis'
    #     return urls




lens = ModelAdmin()
setattr(lens, 'post_before', utils.post_before)
setattr(lens, 'patch_before', utils.patch_before)
setattr(lens, 'valid_after', utils.valid_after)
setattr(lens, 'patch_save', utils.patch_save)