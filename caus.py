import math
from elasticity import Elasticity
from typing import Optional, Tuple


class CAUS:
    """
    Base class for all kinds of custom autoscalers.
    """

    def calculate_replicas(
        self, publishing_rate: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """
        Calculate the amount of desired replicas and buffered replicas given the measured publishing rate and the current amount of replicas.
        """
        pass


class SimpleCAUS(CAUS):
    def __init__(self, elasticity: Elasticity):
        self.elasticity = elasticity

    def adjust_buffers(
        self,
        publishing_rate: float,
        current_replicas: int,
        current_buffers: int,
        current_metric_performance: float,
        buffer_threshold: float,
        initial_buffer: int,
    ) -> int:
        """
        adjust_buffers returns the new buffer size depending on the current publishing rate
        publishing_rate            -  the measured publishing rate
        current_capacity           -  this is the total number of allocated instances
        current_buffers            -  this is the current buffer size
        current_metric_performance -  this is the performance metric
        buffer_threshold           -  the threshold above which to increase the buffer size
        initial_buffer
        """
        usage = publishing_rate / (
            (current_replicas - current_buffers) * current_metric_performance
        )

        # if the usage is touching the buffer check how much
        if usage > 1:
            difference = publishing_rate - (
                (current_replicas - current_buffers) * current_metric_performance
            )
            buffer_usage = difference / (current_buffers * current_metric_performance)
            return current_buffers + (
                buffer_usage > buffer_threshold / 100.0
            )  # either current buffers or current buffers + 1
        else:
            # if usage is less than we need to scale down the buffer
            return max(initial_buffer, current_buffers - 1)

    def calculate_base_workload(
        self, publishing_rate: float, current_metric_performance: float
    ) -> int:
        """
        calculate_base_workload calculates the base work load needed to cope with current publishing rate calculation methods
        """
        return math.ceil(publishing_rate / current_metric_performance)

    def calculate_replicas(
        self, publishing_rate: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """
        calculate_replicas for the given publishing Rate it will either return:
        - the minimum capacity if the publishingRate is less than the capacity
        - current number of replicas allocated
        - the maximum capacity if the workload+buffer exceeds the limit
        """
        # minimum capacity
        if publishing_rate < self.elasticity.capacity:
            return (
                self.elasticity.min_replicas or 1
            ) + self.elasticity.initial_buffer, self.elasticity.initial_buffer

        # Current capacity
        base_workload = self.calculate_base_workload(
            publishing_rate, self.elasticity.capacity
        )

        # adjust anticipation
        buffer_size = self.adjust_buffers(
            publishing_rate,
            current_replicas,
            self.elasticity.buffered_replicas or self.elasticity.initial_buffer,
            self.elasticity.capacity,
            self.elasticity.buffer_threshold,
            self.elasticity.initial_buffer,
        )
        total_replicas = base_workload + buffer_size

        # maximum capacity
        if (
            self.elasticity.max_replicas == None
            or total_replicas > self.elasticity.max_replicas
        ):
            return self.elasticity.max_replicas, self.elasticity.initial_buffer
        return total_replicas, buffer_size
