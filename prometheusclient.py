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

    def get_current_metric_value(self) -> str:
        """Returns the current value of the queried metric.

        For legacy reasons from the original CAUS, it defaults to the query
        'kafka_server_brokertopicmetrics_messagesinpersec_oneminuterate{service="kafka-jmx-metrics",topic="test-topic"}'
        which measures the average amount of messages received per second over a period of one minute.

        Returns:
            The current value of the queried metric as a string.
        """
        metric_data: List = self.prom.custom_query(
            query=get_config()["prometheus"].get(
                "query",
                'kafka_server_brokertopicmetrics_messagesinpersec_oneminuterate{service="kafka-jmx-metrics",topic="test-topic"}',
            ),
        )
        return metric_data[0]["value"][1]
