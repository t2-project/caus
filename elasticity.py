class Elasticity:
    
    def __init__(self, capacity=10.0, min_replicas=None, max_replicas=None, initial_buffer=1, buffered_replicas=0, buffer_threshold=30.0):
        self.capacity = capacity
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.initial_buffer = initial_buffer
        self.buffered_replicas = buffered_replicas
        self.buffer_threshold = buffer_threshold

