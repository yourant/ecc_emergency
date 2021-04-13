import datetime,random
from elasticsearch import Elasticsearch


ELASTICSEARCH = {
    # "hosts": "192.168.101.100:9200",
    "hosts": ["127.0.0.1:9200"],
    "username": "elastic",
    # "username": "ecc_emergency",
    "password": "changeme",
    # "password": "wonders,1",
    "index_map": {
        "data": "data",
        "record_data": "record_data",
        "deleted_data": "deleted_data"
    }
}

es = Elasticsearch(hosts=ELASTICSEARCH["hosts"],
                   # sniff_on_start=True,
                   # # refresh nodes after a node fails to respond
                   # sniff_on_connection_fail=True,
                   # # and also every 60 seconds
                   # sniffer_timeout=12,
                   http_auth=(
                       ELASTICSEARCH["username"], ELASTICSEARCH["password"])
                   )

# doc = {
#     'author': 'nut',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.datetime.now(),
# }

doc = {
        "hash_id": "567uhvcdfghu",
        "occurrence_time": datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'),
        "storage_timestamp": "1592479851.062",
        "is_checkbox": True,
        "summary": "!!!在生产环境部署本项目请将settings中DEBUG设置为False",
        "mastertid": "告警事件的告警组",
        "contact": "联系人:12345678901,联系人:12345678901,联系人:12345678901,",
        "is_import": None,
        "operation": 1,
        "swapiden": "告警类型",
        "tally": 1,
        "ntlogged": 2,
        "dep": 9999,
        "first_occurrence": "3442371892",
        "last_occurrence": "3242371892",
        "severity": 1,
        "server_name": "告警来源",
        "bapp_system": "告警机器所属系统",
        "level": 20,
        "operator": "",
        "jyresult": "",
        "node": "127.0.0.1",
        "confirm_msg": None,
        "state_change": "事件入库时间戳",
        "system": "告警系统(来源)",
        # "system_cn": random.randrange(1, 6),
        "system_cn": random.choice(['系统01', '系统02', '系统03']),
        "acknowledged": "",
        "identifier": "",
        # "group": ""
        # "group": "3"
    }
# print('es', type(es), es)
res = es.index(index="emergencyomnibus", id=7, body=doc)
print('index',res['result'])

res = es.get(index="emergencyomnibus", id=7)
print('get',res['_source'])

# es.indices.refresh(index="test-index")

# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# print("Got %d Hits:" % res['hits']['total']['value'])
# for hit in res['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
