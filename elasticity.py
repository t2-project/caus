from typing import Optional

class Elasticity:

    def __init__(self,
            capacity: float = 10.0,
            min_replicas: Optional[int] = None,
            max_replicas: Optional[int] = None,
            initial_buffer: int = 1,
            buffered_replicas: int = 0,
            buffer_threshold: float = 30.0):
        self.capacity: float = capacity
        self.min_replicas: Optional[int] = min_replicas
        self.max_replicas: Optional[int] = max_replicas
        self.initial_buffer: int = initial_buffer
        self.buffered_replicas: int = buffered_replicas
        self.buffer_threshold: float = buffer_threshold

