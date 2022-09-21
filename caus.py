import math
from elasticity import Elasticity
class CAUS:
    """
    Base class for all kinds of custom autoscalers.
    """
    pass


class SimpleCAUS(CAUS):

    def __init__(self, elasticity: Elasticity):
        self.elasticity = elasticity

    def adjustBufferAmount(self, publishingRate, currentReplicas, currentBuffer, currentPerf,bufferThreshold,initialBuffer):
        """
        AdjustBufferAmount adjusts the buffer size depending on the current publishing rate
        publishingRate            -  the measured publishing rate
        currentCapacity allocated -  this is the total number of allocated instances
        currentBuffer             -  this is the current buffer size
        currentPerf               -  this is the performance metric
        bufferThreshold           -  the threshold to increase the buffer size
        """
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

    def calcBaseWorkload(self,publishingRate, currentPerf):
        """
        Baseworkload calculates the base work load needed to cope with current publishing rate calculation methods
        """
        return math.ceil(publishingRate / currentPerf)

    def calcReplicas(self, publishingRate, currentReplicas):
        """
        CalcReplicas for the given publishing Rate it will either return:
        - the minimum capacity if the publishingRate is less than the capacity
        - current number of replicas allocated
        - the maximum capacity if the workload+buffer exceeds the limit
        The logic behind the controller
        """
        # minimum capacity
        if publishingRate < self.elasticity.capacity:
            minReplicas = self.elasticity.min_replicas if self.elasticity.min_replicas > 0 and self.elasticity.min_replicas != None else 1
            return minReplicas + self.elasticity.initial_buffer, self.elasticity.initial_buffer

        bufferForCalc = self.elasticity.initial_buffer if self.elasticity.buffered_replicas == 0 else self.elasticity.buffered_replicas

        # Current capacity
        baseWorkload = self.calcBaseWorkload(publishingRate, self.elasticity.capacity)

        # adjust anticipation
        bufferSize = self.adjustBufferAmount(
                publishingRate,
                currentReplicas,
                bufferForCalc,
                self.elasticity.capacity,
                self.elasticity.buffer_threshold,
                self.elasticity.initial_buffer
                )
        totalReplicas = baseWorkload + bufferSize

        # maximum capacity
        if self.elasticity.max_replicas == None or totalReplicas > self.elasticity.max_replicas:
            return self.elasticity.max_replicas, self.elasticity.initial_buffer
        return totalReplicas, bufferSize
