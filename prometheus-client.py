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

    def getMetricData():
        metric_data = self.prom.get_current_metric_value(
            metric_name='up',
        )
        metric_df = MetricSnapshotDataFrame(metric_data)
        print(metric_df.head())
