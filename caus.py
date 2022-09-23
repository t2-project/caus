import math
from elasticity import Elasticity
from typing import Optional, Tuple


class CAUS:
    """Abstract base class for all kinds of custom autoscalers."""

    def calculate_replicas(
        self, publishing_rate: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """Calculates the amount of desired replicas and buffered replicas given the current state.

        Args:
            publishing_rate: the measured publishing rate.
            current_replicas: the current amount of replicas.

        Returns:
            A tuple containing both the desired replicas (might be None or an actual value), and the amount of buffered replicas (cannot be None), in that order.
        """
        pass


class SimpleCAUS(CAUS):
    def __init__(self, elasticity: Elasticity):
        self.elasticity = elasticity

    def calculate_new_buffer_size(
        self,
        publishing_rate: float,
        current_replicas: int,
        current_buffers: int,
        current_metric_performance: float,
        buffer_threshold: float,
        initial_buffers: int,
    ) -> int:
        """Returns the new buffer size depending on the current state.

        At the moment, the returned buffer size will be one of 'current_buffers + {-1, 0, 1}'.

        Args:
            publishing_rate: the measured publishing rate.
            current_capacity: the total number of allocated instances.
            current_buffers: the current buffer size.
            current_metric_performance: the measured metric.
            buffer_threshold: the threshold above which to increase the buffer size.
            initial_buffers: the amount of buffers present initially.

        Returns:
            the new buffer size.
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
            return max(initial_buffers, current_buffers - 1)

    def calculate_minimum_replicas(
        self, publishing_rate: float, capacity: float
    ) -> int:
        """Calculates the minimal amount of replicas needed to cope with current publishing rate calculation methods.

        Args:
            publishing_rate: the measured publishing rate.
            capacity: the capacity of this CAUS.

        Returns:
            The minimal amount of replicas needed.
        """
        return math.ceil(publishing_rate / capacity)

    def calculate_replicas(
        self, publishing_rate: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """Calculates the amount of desired replicas and buffered replicas given the current state.

        This method currently returns
            - the min replicas if publishing_rate < capacity.
            - the max replicas if unbuffered replicas + buffered replicas > elasticity.max_replicas.
            - the current number of replicas allocated otherwise.

        Args:
            publishing_rate: the measured publishing rate.
            current_replicas: the current amount of replicas.

        Returns:
            A tuple containing both the desired replicas (might be None or an actual value), and the amount of buffered replicas (cannot be None), in that order.
        """
        # minimum capacity
        if publishing_rate < self.elasticity.capacity:
            return (
                self.elasticity.min_replicas or 1
            ) + self.elasticity.initial_buffer, self.elasticity.initial_buffer

        # Current capacity
        base_workload = self.calculate_minimum_replicas(
            publishing_rate, self.elasticity.capacity
        )

        # adjust anticipation
        buffer_size = self.calculate_new_buffer_size(
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
