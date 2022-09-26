import math
from elasticity import Elasticity
from typing import Optional, Tuple


class CAUS:
    """Abstract base class for all kinds of custom autoscalers."""

    def calculate_replicas(
        self, current_metric_performance: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """Calculates the amount of desired replicas and buffered replicas given the current state.

        Args:
            current_metric_performance: the current value of the measured metric.
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
        current_metric_performance: float,
        current_replicas: int,
        current_buffers: int,
        capacity: float,
        buffer_threshold: float,
        initial_buffers: int,
    ) -> int:
        """Returns the new buffer size depending on the current state.

        At the moment, the returned buffer size will be one of 'current_buffers + {-1, 0, 1}'.

        Args:
            current_metric_performance: the current value of the measured metric.
            current_capacity: the total number of allocated instances.
            current_buffers: the current buffer size.
            capacity: the capacity of this CAUS.
            buffer_threshold: the threshold above which to increase the buffer size.
            initial_buffers: the amount of buffers present initially.

        Returns:
            the new buffer size.
        """
        usage = current_metric_performance / (
            (current_replicas - current_buffers) * capacity
        )

        # if the usage is touching the buffer check how much
        if usage > 1:
            difference = current_metric_performance - (
                (current_replicas - current_buffers) * capacity
            )
            buffer_usage = difference / (current_buffers * capacity)
            return current_buffers + (
                buffer_usage > buffer_threshold / 100.0
            )  # either current buffers or current buffers + 1
        else:
            # if usage is less than we need to scale down the buffer
            return max(initial_buffers, current_buffers - 1)

    def calculate_minimum_replicas(
        self, current_metric_performance: float, capacity: float
    ) -> int:
        """Calculates the minimal amount of replicas needed to cope with the current metric performance.

        Args:
            current_metric_performance: the current value of the measured metric.
            capacity: the capacity of this CAUS.

        Returns:
            The minimal amount of replicas needed.
        """
        return math.ceil(current_metric_performance / capacity)

    def calculate_replicas(
        self, current_metric_performance: float, current_replicas: int
    ) -> Tuple[Optional[int], int]:
        """Calculates the amount of desired replicas and buffered replicas given the current state.

        This method currently returns
            - the min replicas if current_metric_performance < capacity.
            - the max replicas if unbuffered replicas + buffered replicas > elasticity.max_replicas.
            - the current number of replicas allocated otherwise.

        Args:
            current_metric_performance: the current value of the measured metric.
            current_replicas: the current amount of replicas.

        Returns:
            A tuple containing both the desired replicas (might be None or an actual value), and the amount of buffered replicas (cannot be None), in that order.
        """
        # minimum capacity
        if current_metric_performance < self.elasticity.capacity:
            return (
                self.elasticity.min_replicas or 1
            ) + self.elasticity.initial_buffer, self.elasticity.initial_buffer

        # Current capacity
        base_workload = self.calculate_minimum_replicas(
            current_metric_performance, self.elasticity.capacity
        )

        # adjust anticipation
        buffer_size = self.calculate_new_buffer_size(
            current_metric_performance,
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
