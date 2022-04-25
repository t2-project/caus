from controller import controller
from elasticity import elasticity
from multiprocessing import Process, Manager
from rest import API

def main():
    #with Manager() as manager:
    myElasticity = elasticity(elasticityCapacity=8, elasticityMinReplicas=1,elasticityMaxReplicas=10, elasticityBufferThreshold=50.0, elasticityBufferInitial=1, elasticityBufferedReplicas=1)
    myController = controller(myElasticity)
    myController.start()
    #p1 = Process(target=API.app.run)
    #p2 = Process(target=myController.start)
    #p1.start()
    #p2.start()

if __name__ == '__main__':
    main()
