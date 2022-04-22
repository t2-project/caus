#import datetime
#import time
#import requests
#
##prometheus access url
#PROMETHEUS = 'http://prometheus.master.zilchms.de/'
##PROMETHEUS = 'http://10.233.28.132:9090/'
#
##example API request
#response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': 'container_cpu_user_seconds_total'})
#result = response.json()['data']['result']
#
#print(result)

from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame

class prometheusMonitor:

    def __init__(self, url="http://prometheus.master.zilchms.de/"):
        self.prom = PrometheusConnect(url=url, disable_ssl=True)

    def getMessagesInPerSec_OneMinuteRate(self):
        metric_data = self.prom.custom_query(
                query='kafka_server_brokertopicmetrics_messagesinpersec_oneminuterate{service="kafka-jmx-metrics",topic="test-topic"}',
        )
        return metric_data[0]['value'][1]

