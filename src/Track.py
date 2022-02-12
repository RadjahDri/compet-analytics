### CLASSES
class Track:
    def __init__(self, pilotName, date, gpsReference, trackPoints):
        self.pilotName = pilotName
        self.date = date
        self.gpsReference = gpsReference
        self.trackPoints = trackPoints

    def __repr__(self):
        return "%s %s %s %d points" % (self.pilotName, self.date.strftime("%d/%m/%Y"), self.gpsReference, len(self.trackPoints))

    def searchPointInTurnpoint(self, turnpoint, notBeforeTime=None, notAfterTime=None):
        idx = -1
        for trackPoint in self.trackPoints:
            idx += 1
            if(notAfterTime and trackPoint.time > notAfterTime):
                break

            if(notBeforeTime and trackPoint.time < notBeforeTime):
                continue

            # TOREM
            #from geopy.distance import great_circle
            #tmp = great_circle(turnpoint.coordinates.toDegree(), trackPoint.coordinates.toDegree()).m
            #print("%s %d %s %s" % (trackPoint.time, tmp, turnpoint.coordinates, trackPoint.coordinates))
            if(turnpoint.isContainTrackPoint(trackPoint)):
                return idx


        return None
