import math
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

    def __init__(self, elasticityCapacity=0.0, elasticityMinReplicas=None, elasticityMaxReplicas=None, elasticityBufferInitial=0,elasticityBufferedReplicas=0,elasticityBufferThreshold=70.0):
        self.elasticityCapacity = elasticityCapacity
        self.elasticityMinReplicas = elasticityMinReplicas
        self.elasticityMaxReplicas = elasticityMaxReplicas
        self.elasticityBufferInitial = elasticityBufferInitial
        self.elasticityBufferReplicas = elasticityBufferReplicas
        self.elasticityBufferThreshold = elasticityBufferThreshold


    # AdjustBufferAmount adjusts the buffer size depending on the current publishing rate
    # publishingRate            -  the measured publishing rate
    # currentCapacity allocated -  this is the total number of allocated instances
    # currentBuffer             -  this is the current buffer size
    # currentPerf               -  this is the performance metric
    # bufferThreshold           -  the threshold to increase the buffer size
    def adjustBufferAmount(publishingRate, currentReplicas, currentBuffer, currentPerf,bufferThreshold,initialBuffer):
        usage = publishingRate/((currentReplicas - currentBuffer)*currentPerf)
        bufferThresh = bufferThreshold / 100.0

        #if the usage is touching the buffer check how much
        if usage > 1:
            difference = publishingRate - ((currentReplicas - currentBuffer) * currentPerf
            bufferUsage = difference / (currentBuffer * currentPerf)
            if bufferUsage > bufferThresh:
                return currentBuffer+1
        else:
            #if usage is less than we need to scale down the buffer
            return max(initialBuffer, currentBuffer-1)
        return currentBuffer

    # Baseworkload calculates the base work load needed to cope with current publishing rate calculation methods
    def baseWorkload(publishingRate, currentPerf):
        return math.ceil(publishingRate / currentPerf)

    # CalcReplicas for the given publishing Rate it will either return:
    # - the minimum capacity if the publishingRate is less than the capacity
    # - current number of replicas allocated
    # - the maximum capacity if the workload+buffer exceeds the limit
    # The logic behind the controller
    def calcReplicas(publishingRate, currentReplicas)
        # minimum capacity
        if publishingRate < elasticityCapacity:
            minReplicas = 1
            if elasticityMinReplicas != 0 and elasticityMinReplicas != None:
                minReplicas = elasticityMinReplicas
            return minReplicas + elasticityBufferInitial, elasticityBufferInitial

        # bufferForCalc
        if elasticityBufferedReplicas == 0:
            bufferForCalc = elasticityBufferInitial
        else:
            bufferForCalc = elasticityBufferedReplicas

        # Current capacity
        baseWorkload = baseWorkload(publishingRate, elasticityCapacity)
        # adjust anticipation
        bufferSize = adjustBufferAmount(publishingRate, currentReplicas, bufferForCalc, elasticityCapacity, elasticityBufferThreshold, elasticityBufferInitial)
        totalReplicas = baseWorkload + bufferSize

        # maximum capacity
        if totalReplicas > elasticityMaxReplicas:
            totalReplicas = elasticityMaxReplicas
            bufferSize = elasticityBufferInitial
        return totalReplicas, bufferSize
