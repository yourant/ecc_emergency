import random

# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from pytz import utc

from apps.emergency.schedules import tasks


# 生成非阻塞调度器
# scheduler = BackgroundScheduler()

# 生成复杂非阻塞调度器
jobstores = {
    'default': MemoryJobStore()
}
executors = {
    # 'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(4)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 1
}
scheduler = BackgroundScheduler(job_defaults=job_defaults, timezone=utc)


# 清除残留任务: 解决django重启时残留的任务
# scheduler.remove_all_jobs()


# 添加简单调度任务、定时任务
# scheduler.add_job(tasks.emergencyomnibusrule)
# scheduler.add_job(tasks.emergencyomnibusrule02)
# scheduler.add_job(tasks.emergencyomnibusrule03)
# scheduler.add_job(tasks.emergencyomnibusrule, 'interval',
#                   seconds=random.randint(2, 6), max_instances=10, jitter=99)
# scheduler.add_job(tasks.post_omnibus)
# scheduler.add_job(tasks.emergencyomnibus)
# scheduler.add_job(tasks.emergencyomnibus, 'interval',
#                   seconds=random.randint(1, 6), max_instances=10, jitter=99)
# scheduler.add_job(tasks.emergencyovertime, 'interval',
#                   seconds=10, max_instances=10,)

# 添加复杂调度任务、定时任务

# scheduler.add_job(tasks.emergencyomnibus, id='emergencyomnibus',
#     trigger='interval', seconds=10, replace_existing=True)
# scheduler.add_job(tasks.emergencyovertime, id='emergencyovertime',
#     trigger='interval', seconds=10, replace_existing=True)

# scheduler.add_job(tasks.task01, id='job_interval',
#     trigger='interval', seconds=5, replace_existing=True)
# scheduler.add_job(tasks.task01, id='job_cron',
#     trigger='cron', month='4-8,11-12', hour='7-11', second='*/10', end_date='2018-05-30')
# scheduler.add_job(tasks.task01, id='job_once_now')
# scheduler.add_job(tasks.task01, id='job_date_once',
#     trigger='date', run_date='2018-04-05 07:48:05')
# scheduler.add_job(tasks.consume_omnibus_overtime, id='job_once_now')  # kafka消费任务

# 测试代码
# from types import MethodType, FunctionType
# for attr in dir(tasks):
#     if isinstance(getattr(tasks, attr), FunctionType):
#         print(attr, type(getattr(tasks, attr)))
# print('scheduler.state', scheduler.state, scheduler.get_jobs())
# scheduler.shutdown()
# scheduler.remove_job('emergencyomnibus')
# scheduler.remove_job('emergencyovertime')
# scheduler._executors.clear()
# scheduler._jobstores.clear()

# 执行调度任务、定时任务
scheduler.start()

# print('scheduler.state', scheduler.state, scheduler.get_jobs())
