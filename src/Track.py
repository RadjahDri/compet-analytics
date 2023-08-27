import datetime


### CONSTANTS
MAX_GLIDER_SPEED_IN_KMH = 100
MAX_GLIDER_SPEED_IN_MS = int(MAX_GLIDER_SPEED_IN_KMH / 3.6)


### CLASSES
class Track:
    def __init__(self, pilotName, gliderName, date, gpsReference, trackPoints):
        self.pilotName = pilotName
        self.gliderName = gliderName
        self.date = date
        self.gpsReference = gpsReference
        self.trackPoints = trackPoints
        self.beginTime = min(trackPoints.keys())
        self.endTime = max(trackPoints.keys())


    def __repr__(self):
        return "%s %s %s from %s to %s %d points" % (self.pilotName, self.gliderName, self.date.strftime("%d/%m/%Y"), self.beginTime.strftime("%H:%M:%S"), self.endTime.strftime("%H:%M:%S"), len(self.trackPoints))


    def searchPointInTurnpoint(self, turnpoint, notBeforeTime, notAfterTime):
        bStop = False
        minTimeIdx = 0
        maxTimeIdxPersistente = len(self.trackPoints)-1


        currentTrackPoint = self.getPointAtTime(notBeforeTime)
        while(currentTrackPoint.time < notAfterTime):
            if(turnpoint.isContainTrackPoint(currentTrackPoint)):
                    return currentTrackPoint

            distanceToTurnpoint =  currentTrackPoint.coordinates.computeDistance(turnpoint.coordinates) - (turnpoint.radius * 1.005)
            minTimeToNextTurnpoint = distanceToTurnpoint // MAX_GLIDER_SPEED_IN_MS
            if(minTimeToNextTurnpoint > 0):
                notBeforeTime = addTimes(currentTrackPoint.time, minTimeToNextTurnpoint)

            currentTrackPoint = self.getPointAtTime(notBeforeTime)
            if(not currentTrackPoint):
                return None

            notBeforeTime = addTimes(currentTrackPoint.time, 1)

        return None



    def getPointAtTime(self, time):
        while(self.beginTime <= time and time <= self.endTime and not self.trackPoints.get(time)):
            time = addTimes(time, 1)

        if(self.beginTime > time or time > self.endTime):
            return None

        return self.trackPoints[time]




### FUNCTIONS
def addTimes(time, seconds):
    return (datetime.datetime(1,1,1,time.hour, time.minute, time.second) + datetime.timedelta(0, seconds)).time()
