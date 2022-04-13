class elasticity:
    
    def __init__(self, elasticityCapacity=10.0, elasticityMinReplicas=None, elasticityMaxReplicas=None, elasticityBufferInitial=1,elasticityBufferedReplicas=0,elasticityBufferThreshold=30.0):
        self.elasticityCapacity = elasticityCapacity
        self.elasticityMinReplicas = elasticityMinReplicas
        self.elasticityMaxReplicas = elasticityMaxReplicas
        self.elasticityBufferInitial = elasticityBufferInitial
        self.elasticityBufferedReplicas = elasticityBufferedReplicas
        self.elasticityBufferThreshold = elasticityBufferThreshold

