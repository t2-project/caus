from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
from config import get_config

class prometheusMonitor:

    def __init__(self, url=get_config()['prometheus']['url']):
        self.prom = PrometheusConnect(url=url, disable_ssl=True)

    def getMessagesInPerSec_OneMinuteRate(self):
        metric_data = self.prom.custom_query(
                query=get_config()['prometheus'].get('query','kafka_server_brokertopicmetrics_messagesinpersec_oneminuterate{service="kafka-jmx-metrics",topic="test-topic"}'),
        )
        return metric_data[0]['value'][1]

