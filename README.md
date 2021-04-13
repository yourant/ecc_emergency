开发框架2.0使用说明：https://docs.bk.tencent.com/blueapps/USAGE.html


# 测试接口说明

## 准备工作: 首先启动项目

### 1. 拉取内网仓库dev分支代码
git remote add yuxin git@192.168.251.183:HXB/ecc_emergency.git
git clone git@192.168.251.183:HXB/ecc_emergency.git -b dev

### 2. 安装依赖项
1. 本地环境需安装redis并启动
2. pip install requirements.txt

### 3. 启动项目
迁移 + 启动
python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000


### 模拟kafka数据连续推送(可选)
启动模拟kafka数据连续推送后的逻辑流程: 
1. 每30s生成一条'告警'数据 
2. 根据'告警'数据生成一条'综合类告警数据聚合'数据
3. 根据'告警聚合'字段status的状态 实时向'告警聚合'前端WebSocket接口推送数据
4. 前端提交关联事件操作 生成事件与发送企业微信提醒

#### celery方式（已废弃）
1. 启动celery定时任务的worker
python manage.py celery worker -l info
2. 启动celery定时任务: 向综合类告警连续新增数据
python manage.py celery beat -l info

#### APSchedule（建议使用此方式）
在apps/emergency/schedules/__init__.py中打开已定义的任务



## API接口

### WebSocket接口: 向前端实时推送
#### 综合类告警聚合:
url: ws://localhost:8000/ws/emergencyomnibusgroup/
#### 交易类告警聚合:
url: ws://localhost:8000/ws/emergencyovertimegroup/

### HTTP接口: 更改告警聚合状态: 对应前端的<执行>操作
  1. 通知负责人(当前版本暂不支持)
  2. 关联事件(已支持)
  3. 企业微信通知(已支持)

url: 
  综合类: http://localhost:8000/api/v1/emergency/emergencyomnibusgroup/<id>
  交易类: http://localhost:8000/api/v1/emergency/emergencyovertimegroup/<id>
method: PATCH
content-type: 'application/json'
{
    "status": 1,  # int, 必须项, 更改聚合数据的状态, 对应关系(0, "未处理"), (1, "已通知 未处理"), (2, "已处理")
    "notify_list": [ # list/array, 可选项, 发送企业微信通知的开关
      "wecom_appchat", # 发送企业微信通知（群）
      "wecom_message" # 发送企业微信通知（处理人）
      ],
    "event": { # object/dict, 可选项 
      "level": 0, # int, 可选, 事件级别, 对应关系(0, "A"), (1, "B"), (2, "C"), (3, "D")
      "number": 3456789012 # string, 可选项, 事件单号 ,
      "dealer_list": ["DongFangFang", "WoKeZhenShanLiang"] # list/array, 可选项, 事件处理人列表,
  }
}


## 封装的HTTP通用接口(手动增删改查):
  事件: /api/v1/emergency/event/
  综合类: /api/v1/emergency/emergencyomnibus/
  交易类: /api/v1/emergency/emergencyovertime/
  综合类聚合: /api/v1/emergency/emergencyomnibusgroup/
  交易类聚合: /api/v1/emergency/emergencyovertimegroup/
  offset: /api/v1/emergency/offsetmodel/

### GET: 定义查询条件 无query条件则返回全表所有数据（分页方式）
method: GET
query:
  {
    'pk': 1,    # (int/string) 获取指定主键的那条数据
    'q': 1, # (int/strin) 模糊搜索全表字段 或search_list中规定的字段范围
    'max': 'id', # (string) 返回指定字段的最大值的那条数据
    'min': 'id', # (string) 返回指定字段的最小值的那条数据
    '当前model的任意字段名': '任意值', # 返回匹配任意字段名与任意值的那条数据
    'page': '2',  # (int) 任意整数 返回指定分页页码的50条数据
  }

### POST: 在data中以dict定义每个字段的值 因为是增加数据因此不支持定义pk
method: POST
content-type: 'application/json'
data: 
  综合类:
    {
      "hash_id": "123456qwert",
      "summary": "作业流qwert123456中的作业qwert123456运行出错,请注意!",
      "storage_timestamp": "1602479851.062",
      "is_checkbox": True,
      "mastertid": "告警事件的告警组",
      "contact": '操作室值班人员',
      "is_import": True,
      "operation": 1,
      "swapiden": "HXB_123456qwert",
      "tally": 1,
      "ntlogged": 2,
      "dep": 9999,
      "first_occurrence": "2022-12-21 13:10:22",
      "last_occurrence": "2022-12-23 18:00:02",
      "severity": 1,
      "server_name": "告警来源",
      "bapp_system": "告警机器所属系统",
      "url": 20,
      "operator": "",
      "jyresult": "",
      "node": "127.0.0.1",
      # "confirm_msg": "告警事件处理信息(预留字段 不建议存值 留空即可）",
      "confirm_msg": None,
      "system": "00338",
      "system_cn": "一体化运维管理系统",
      "acknowledged": "",
      "identifier": "",
    }
  交易类:
    {
      "is_checkbox": True,
      "hash_id": "123456qwert",
      "storage_timestamp": "1602479851.062",
      "start_time": "10:13:00",
      "end_time": "10:23:00",
      "error_count": 121,
      "system": "76290wq",
      "system_cn": "告警渠道(来源)",
      "qudao": "ABSC12345",
      "qudao_cn": "影像前端系统",
      "server": "NBEA123456",
      "server_cn": "BEAI系统",
      "branch_cn": "机构码翻译",
      "code": "S00130123456",
      "code_cn": "交易码翻译S001303123456",
      "rtcode": "ESB-E-123456",
      "rtcode_cn": "超时未得到服务系统应答",
      "key": "dbapp009-rtyu-20201012123456-123456",
      "route": "路由",
    }

### PATCH: data中以dict定义要修改字段的值

### DELETE: data中以dict定义pk 不可定义其它字段



## 微信企业通知代码整合位置及测试说明

#### 微信企业通知逻辑代码整合位置
apps/emergency/backends/notify.py 文件中的WeCom.send方法中
目前调用时仅打印一行中文, 将已调通的企业微信通知逻辑代码整合到WeCom.send方法即可。

#### 测试
已整合到项目流程中 请参考以上“API接口 > HTTP接口”


## 移动页
### 事件处理
http://paas.hsmix.com/o/bk_ecc_emergency/m/#/emergency/event/<id>

##历史数据导出
综合类：http://127.0.0.1:8000/api/export/?type=omnibus
交易类：http://127.0.0.1:8000/api/export/?type=overtime

##联系人信息接口
http://127.0.0.1:8000/api/telephone/?keyword=姓名
{"employes": [{"StaffName": "\u674e\u9633", "Mobile": "18888888888", "Company": "\u534e\u590f\u94f6\u884c", "OrgName": "\u751f\u4ea7\u8fd0\u884c\u5ba4", "Account": "zhliyang1"}]}

##系统负责人接口
http://127.0.0.1:8000/api/SystemManager/?keyword=系统名称
{"staff": [{"Account": "zhwangl", "StaffName": "\u738b\u4eae"}, {"Account": "zhliyang1", "StaffName": "\u674e\u9633"}]}
