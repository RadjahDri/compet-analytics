### CLASSES
class Track:
    def __init__(self, pilotName, gliderName, date, gpsReference, trackPoints):
        self.pilotName = pilotName
        self.gliderName = gliderName
        self.date = date
        self.gpsReference = gpsReference
        self.trackPoints = trackPoints

        self.lastSearchTime = trackPoints[0].time
        self.lastSearchIdx = 0


    def __repr__(self):
        return "%s %s %s %d points" % (self.pilotName, self.date.strftime("%d/%m/%Y"), self.gpsReference, len(self.trackPoints))


    def searchPointInTurnpoint(self, turnpoint, notBeforeTime=None, notAfterTime=None):
        if(notBeforeTime < self.lastSearchTime):
            self.lastSearchTime = self.trackPoints[0].time
            self.lastSearchIdx = 0
        for trackPoint in self.trackPoints[self.lastSearchIdx:]:
            self.lastSearchIdx += 1
            if(notAfterTime and trackPoint.time > notAfterTime):
                break

            if(notBeforeTime and trackPoint.time < notBeforeTime):
                continue

            if(turnpoint.isContainTrackPoint(trackPoint)):
                self.lastSearchTime = trackPoint.time
                return self.lastSearchIdx

        self.lastSearchTime = self.trackPoints[0].time
        self.lastSearchIdx = 0
        return None
