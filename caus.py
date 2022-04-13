import math
from elasticity import elasticity
class CAUS:

# vars for parameterization of elasticity, commented out in order to be instance variables instead of class variables
# in order to not have side effect regarding multiple mutable objects
# elastic capacity: float
#elasticityCapacity = 0.0
# elastic min replicas: int or None
#elasticityMinReplicas = None
# elastic max replicas: int or None
#elasticityMaxReplicas = None
# elastic initial buffer: int
#elasticityBufferInitial = 0
# elastic buffered replicas: int
#elasticityBufferedReplicas = 0
# elastic buffer threshold: float
#elasticityBufferThreshold = 70.0

#TODO  push elasticity stuff to own class?

    def __init__(self, elasticity):
        self.elasticity = elasticity

    # AdjustBufferAmount adjusts the buffer size depending on the current publishing rate
    # publishingRate            -  the measured publishing rate
    # currentCapacity allocated -  this is the total number of allocated instances
    # currentBuffer             -  this is the current buffer size
    # currentPerf               -  this is the performance metric
    # bufferThreshold           -  the threshold to increase the buffer size
    def adjustBufferAmount(self, publishingRate, currentReplicas, currentBuffer, currentPerf,bufferThreshold,initialBuffer):
        usage = publishingRate/((currentReplicas - currentBuffer)*currentPerf)
        bufferThresh = bufferThreshold / 100.0

        #if the usage is touching the buffer check how much
        if usage > 1:
            difference = publishingRate - ((currentReplicas - currentBuffer) * currentPerf)
            bufferUsage = difference / (currentBuffer * currentPerf)
            if bufferUsage > bufferThresh:
                return currentBuffer+1
        else:
            #if usage is less than we need to scale down the buffer
            return max(initialBuffer, currentBuffer-1)
        return currentBuffer

    # Baseworkload calculates the base work load needed to cope with current publishing rate calculation methods
    def calcBaseWorkload(self,publishingRate, currentPerf):
        return math.ceil(publishingRate / currentPerf)

    # CalcReplicas for the given publishing Rate it will either return:
    # - the minimum capacity if the publishingRate is less than the capacity
    # - current number of replicas allocated
    # - the maximum capacity if the workload+buffer exceeds the limit
    # The logic behind the controller
    def calcReplicas(self, publishingRate, currentReplicas):
        # minimum capacity
        if publishingRate < self.elasticity.elasticityCapacity:
            minReplicas = 1
            if self.elasticity.elasticityMinReplicas != 0 and self.elasticity.elasticityMinReplicas != None:
                minReplicas = self.elasticity.elasticityMinReplicas
            return minReplicas + self.elasticity.elasticityBufferInitial, self.elasticity.elasticityBufferInitial

        # bufferForCalc
        if self.elasticity.elasticityBufferedReplicas == 0:
            bufferForCalc = self.elasticity.elasticityBufferInitial
        else:
            bufferForCalc = self.elasticity.elasticityBufferedReplicas

        # Current capacity
        baseWorkload = self.calcBaseWorkload(publishingRate, self.elasticity.elasticityCapacity)
        # adjust anticipation
        bufferSize = self.adjustBufferAmount(publishingRate, currentReplicas, bufferForCalc, self.elasticity.elasticityCapacity, self.elasticity.elasticityBufferThreshold, self.elasticity.elasticityBufferInitial)
        totalReplicas = baseWorkload + bufferSize

        # maximum capacity
        if self.elasticity.elasticityMaxReplicas == None or totalReplicas > self.elasticity.elasticityMaxReplicas:
            totalReplicas = self.elasticity.elasticityMaxReplicas
            bufferSize = self.elasticity.elasticityBufferInitial
        return totalReplicas, bufferSize
