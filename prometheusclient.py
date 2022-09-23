from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
from config import get_config
from typing import List, Union


class PrometheusMonitor:
    def __init__(self, url: str = get_config()["prometheus"]["url"]):
        self.prom = PrometheusConnect(
            url=url,
            disable_ssl=get_config().getboolean(
                "prometheus", "disable-ssl", fallback=True
            ),
        )

    def getMessagesInPerSec_OneMinuteRate(self) -> str:
        """Does something.

        Returns:
            A metric value as string?
        """
        metric_data: List = self.prom.custom_query(
            query=get_config()["prometheus"].get(
                "query",
                'kafka_server_brokertopicmetrics_messagesinpersec_oneminuterate{service="kafka-jmx-metrics",topic="test-topic"}',
            ),
        )
        return metric_data[0]["value"][1]
