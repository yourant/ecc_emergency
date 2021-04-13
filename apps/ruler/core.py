import json
from django.db.models import Q
import rulez
# from rulez import *
from apps.lens.utils import logger, decorator

""" 
Assemble a django "Q" query filter object from a specification that consists 
of a possibly-nested list of query filter descriptions.  These descriptions
themselves specify Django primitive query filters, along with boolean 
"and", "or", and "not" operators.  This format can be serialized and 
deserialized, allowing django queries to be composed client-side and
sent across the wire using JSON.

Each filter description is a list.  The first element of the list is always 
the filter operator name. This name is one of either django's filter 
operators, "eq" (a synonym for "exact"), or the boolean operators
"and", "or", and "not".

Primitive query filters have three elements:

[filteroperator, fieldname, queryarg]

"filteroperator" is a string name like "in", "range", "icontains", etc. 
"fieldname" is the django field being queried.  Any name that django
accepts is allowed, including references to fields in foreign keys
using the "__" syntax described in the django API reference. 
"queryarg" is the argument you'd pass to the `filter()` method in
the Django database API.

"and" and "or" query filters are lists that begin with the appropriate 
operator name, and include subfilters as additional list elements:

['or', [subfilter], ...]
['and', [subfilter], ...] 

"not" query filters consist of exactly two elements:

['not', [subfilter]]

As a special case, the empty list "[]" or None return all elements.

If field_mapping is specified, the field name provided in the spec
is looked up in the field_mapping dictionary.  If there's a match,
the result is subsitituted. Otherwise, the field name is used unchanged
to form the query. This feature allows client-side programs to use
"nice" names that can be mapped to more complex django names. If
you decide to use this feature, you'll probably want to do a similar
mapping on the field names being returned to the client.

This function returns a Q object that can be used anywhere you'd like
in the django query machinery.

This function raises ValueError in case the query is malformed, or
perhaps other errors from the underlying DB code.

Example queries:

['and', ['contains', 'name', 'Django'], ['range', 'apps', [1, 4]]]
['not', ['in', 'tags', ['colors', 'shapes', 'animals']]]
['or', ['eq', 'id', 2], ['icontains', 'city', 'Boston']]

"""


class Mapping(object):
    """docstring for Mapping"""

    LOGIC = {
        'and': '&',
        'or': '|',
        # 'not': 'not',
    }

    OPERATOR = {
        '==': 'exact',
        '!=': 'neq',
        '>': 'gt',
        '>=': 'gte',
        '=>': 'gte',
        '<': 'lt',
        '<=': 'lte',
        '=<': 'lte',
        # 'and': 'and',
        # 'or': 'or',
        'in': 'in',
        'icontains': 'icontains',
        'not': 'not',
        'str': 'str_',
        'int': 'int_',
        '+': 'plus',
        '-': 'minus',
        '*': 'multiply',
        '/': 'divide'
    }

    VERB = {
        'get': 'get',
    }

    FIELD_TYPE = {
        # 'type': 'AutoField',
        # 'type': 'OneToOneField',
        # 'CharField': 'str',
        # 'TextField': 'str',
        # 'SmallIntegerField': 'int',
        # 'IntegerField': 'int',
        # 'FloatField': 'float',
        # 'DateTimeField': 'datetime',
        # 'TimeField': 'time',

        'CharField': {
            'label': '_str',
            'operator': ['+', '-', ]
        },
        'TextField': {
            'label': '_str',
            'operator': []
        },
        'SmallIntegerField': {
            'label': '_int',
            'operator': []
        },
        'IntegerField': {
            'label': '_int',
            'operator': []
        },
        'FloatField': {
            'label': '_float',
            'operator': []
        },
        'DateTimeField': {
            'label': '_datetime',
            'operator': [],
            # 'function': ['']
        },
        'TimeField': {
            'label': '_time',
            'operator': []
        },
    }

    class Function(object):
        """docstring for Function"""

        def __init__(self):
            super(Function, self).__init__()
            # self._float = self._int

        def _int(value, offset):
            try:
                value = int(value)
            except Exception as e:
                raise Exception('参数(value)必须为Number类型')
            try:
                offset = int(offset)
            except Exception as e:
                raise Exception('参数(offset)必须为Number类型')
            return value + offset

        _float = _int

        def _str(value, offset):
            try:
                value += offset
            except Exception as e:
                raise Exception('字符串不支持偏移量(offset)')
            else:
                pass
            finally:
                return value

        def _time(value, offset):
            '''获取与指定时间加上秒数差的时间

            Arguments:
                time {[string]} -- [时间字符串 example: "12:10:50"]
                offset {[int]} -- [秒数差]

            return {[string]} -- [时间字符串 example: "12:10:50"]
            '''
            # print('_time', type(str(value)), str(value))
            import datetime
            FMT = '%H:%M:%S'
            if type(value) != str:
                value = str(value)
            # if type(value) == str:
                value = datetime.datetime.strptime(value, FMT)
                # print('_time', type(value), value)
            time_range = datetime.timedelta(seconds=offset)
            return (value + time_range).strftime(FMT)


class QueryAdmin(object):
    # class QueryAdmin(rulez.Engine):

    """docstring for QueryAdmin"""

    __mapping = Mapping

    def __init__(self, filter_model=None):
        ''' 过滤查询匹配类

        [description]

        Keyword Arguments:
            filter_model {[Model]} -- [过滤标的的model类] (default: {None})
        '''
        super(QueryAdmin, self).__init__()

        # self.data_model = data_model
        # self.data_model.fileds_mapping = self.gen_fileds_mapping(data_model)
        # print('self.data_model', self.data_model.fileds_mapping)

        # self.filter_model = None
        # self.filter_model = filter_model
        # self.filter_model.fileds_mapping = self.gen_fileds_mapping(
        #     filter_model)
        # print('self.fileds_mapping', self.filter_model.fileds_mapping)

        self.models_mapping = {}
        self.app_name = 'ruler'
        self.namespace = 'ruler'
        self.combined_query = None

    def register(self, model_class, lens_config=None):
        """将model和model的config类对应起来
        """
        # if not lens_config:
        # def __init__(self, model_class):
        #     self.model_class = model_class
        # lens_config = type('ModelConfig', (object,),
        #                    {'__init__': __init__, })
        self.models_mapping[model_class._meta.model_name] = model_class

    def gen_fileds_mapping(self, model):
        ''' 生成model字段映射

        [description]

        Arguments:
            model {[Model]} -- [description]
        '''
        return {i.name: {
            'verbose_name': i.verbose_name, 'type': i.get_internal_type()} for i in model._meta.fields if self.__mapping.FIELD_TYPE.get(i.get_internal_type())}

    def verify_rule(self, rule):
        '''校验规则数据结构
        '''
        if rule == None:
            raise Exception('rule字段是必须项')
        if isinstance(rule, str):
            try:
                rule = json.loads(rule)
            except Exception as e:
                raise Exception('规则必须是一个json')
        if type(rule) != dict:
            raise Exception('规则必须是一个json')

        operator = rule.get('operator')
        value = rule.get('value')
        if not operator or not value:
            raise Exception(
                'primitive filters must have two key (operator and value)')
        operator = operator.lower()
        return True

    def combine_rule(self, rule, instance):
        # print('combine_rule --->', rule.get('operator').lower())
        operator = rule.get('operator').lower()
        # rule = rule.get('value')

        if operator in self.__mapping.LOGIC.keys():
            query = self.combine_logic_rule(rule, instance)

        # elif operator in self.__mapping.VERB.keys():
        #     query = self.combine_verb_rule(rule, instance)

        elif operator in self.__mapping.OPERATOR.keys():
            query = self.combine_operator_rule(rule, instance)

        else:
            raise Exception('operator(%s) is not valid.' % operator)

        # print('combine_rule query', query)
        return query

    def combine_logic_rule(self, rule, instance):
        # print('combine_logic_rule --->')

        operator = rule.get('operator').lower()
        combined_query = Q()
        combined_query.connector = operator
        rule_list = rule.get('value')
        if type(rule_list) != list:
            raise Exception('value must is a list')

        return self.combine_list_rule(rule_list, instance, combined_query)

    def combine_list_rule(self, rule_list, instance, combined_query):
        # print('combine_list_rule --->')

        for rule in rule_list:
            # operator = value.get('operator').lower()
            # value = rule.get('value')
            # field = value.get('field')
            # print('for', '-' * 10)
            # q = self.build_rule(rule, instance)
            query = self.combine_rule(rule, instance)
            if query != None:
                # print('combine_list_rule query != None', query)
                if len(query.children) > 1:
                    combined_query.children.append(query)
                else:
                    combined_query.children.extend(query.children)

        # print('combine_list_rule', combined_query)
        return combined_query

    def combine_verb_rule(self, rule, instance):
        # print('<--- combine_verb_rule --->', rule)

        operator = rule.get('operator').lower()
        field = rule.get('field')
        offset = rule.get('offset')
        value = rule.get('value')
        # print(operator, field, offset)

        if operator == 'get':
            if hasattr(instance, field):
                value = getattr(instance, field)

                # 获取字段类型对应的function
                _field = self.fileds_mapping.get(field)
                if not _field:
                    raise Exception('表中没有字段(%s)' % (field))

                field_type = _field.get('type')
                if field_type not in self.__mapping.FIELD_TYPE.keys():
                    raise Exception('字段类型(%s)暂不支持动作(%s)' %
                                    (field_type, operator))
                # print('field_type', field_type)
                func_name = self.__mapping.FIELD_TYPE.get(
                    field_type).get('label')
                func = getattr(self.__mapping.Function, func_name)
                # print('field_type', field_type, func_name, func)
                # print("offset", type(value), value, type(offset), offset)

                # 使用function计算值
                rule['value'] = func(value, offset)
            else:
                raise Exception('model(%s)中无字段(%s)' %
                                (self.filter_model, field))
        return rule['value']

    def combine_operator_rule(self, rule, instance):
        # print('combine_operator_rule', rule)
        # some other query, will be validated in the query machinery
        # ["cmd", "fieldname", "arg"]

        # provide an intuitive alias for exact field equality

        operator = rule.get('operator').lower()
        field = rule.get('field')
        value = rule.get('value')
        if type(value) == dict:
            value = self.combine_verb_rule(value, instance)
            # print('value', value)

        if not field:
            raise(
                ValueError, 'primitive filters must have two arguments (fieldname and query arg)')

        # if self.models:
            # see if the mapping contains an entry for the field
            # (for example, if you're mapping an external database name
            # to an internal django one).  If not, use the existing name.
            # field = self.models.get(field, field)

        kwname = str("%s%s%s" %
                     (field, '__', self.__mapping.OPERATOR.get(operator)))
        kwdict = {kwname: value}
        query = Q(**kwdict)
        # print('combine_operator_rule query', query)
        return query

    def build_rule(self, rule, instance, filter_model=None):
        # print('build_rule', '-' * 10, type(rule), self.filter_model)
        """ [summary]

        [description]

        Arguments:
            rule {[type]} -- [description]

        Keyword Arguments:
            field_mapping {[type]} -- [description] (default: {None)('loop', '-' * 10})
        """

        # 校验规则数据结构
        self.verify_rule(rule)

        # 若无指定过滤标的的model 则使用instance本身的model
        self.filter_model = filter_model or type(instance)
        # print('self.filter_model', self.filter_model)

        # 生成过滤标的的model字段映射
        self.fileds_mapping = self.gen_fileds_mapping(self.filter_model)
        # print('self.fileds_mapping', self.fileds_mapping)

        return self.combine_rule(rule, instance)

    @decorator.timer
    def filter(self, rule, data, filter_model=None):
        # print('filter', hasattr(self, 'compile_condition'))
        from django.db.models import Model
        if isinstance(data, Model):
            # print('filter isinstance(data, Model)', isinstance(data, Model))
            rule = self.build_rule(rule, instance=data,
                                   filter_model=filter_model)
            return self.filter_model.objects.filter(rule).last()

        # logger.info('rule_match_omnibus rule', type(rule), rule)
        engine = rulez.Engine()

        # 使用定义的规则构建规则引擎手柄
        e = engine.compile_condition('native', rule)
        # e = engine.compile_condition('elasticsearch', rule)

        # 使用规则引擎对数据进行匹配
        if isinstance(data, list):
            return filter(lambda i: e(i), data)
        else:
            return e(data)


# rulez.dectate.clean()
# rulez.dectate.commit(rulez.Engine, QueryAdmin)
# rulez.dectate.commit(QueryAdmin)
ruler = QueryAdmin()


setattr(ruler, 'parse_dsl', getattr(rulez, 'parse_dsl'))
# setattr(ruler, 'match', match)


# print(
#     'query',
#     type(query),
#     query,
#     # dir(ruler)
# )
