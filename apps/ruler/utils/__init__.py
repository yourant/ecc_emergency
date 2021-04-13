# import rulez
from apps.lens.utils import logger


# logger.info(omnibus_data, group_data)

# def get_time_range(time):
#     import datetime
#     FMT = '%H:%M:%S'
#     if type(time) == str:
#         time = datetime.datetime.strptime(time, FMT)
#     time_range = datetime.timedelta(seconds=30)
#     return [(time - time_range).strftime(FMT), (time + time_range).strftime(FMT)]


def get_diff_time(time, diff_seconds):
    '''获取与指定时间加上秒数差的时间

    Arguments:
        time {[string]} -- [时间字符串 example: "12:10:50"]
        diff_seconds {[int]} -- [秒数差]

    return {[string]} -- [时间字符串 example: "12:10:50"]
    '''
    import datetime
    FMT = '%H:%M:%S'
    if type(time) == str:
        time = datetime.datetime.strptime(time, FMT)
    time_range = datetime.timedelta(seconds=diff_seconds)
    return (time + time_range).strftime(FMT)

# time_range = get_time_range(omnibus_data['occurrence_time'])
# delay_time = get_delay_time(omnibus_data['occurrence_time'], 60)
# logger.info('delay_time', type(delay_time), delay_time)
