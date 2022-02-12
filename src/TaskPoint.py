from geopy.distance import great_circle

### CLASSES
class TaskPoint:
    def __init__(self, id, coordinates, radius):
        self.id = id
        self.coordinates = coordinates
        self.radius = radius

    def __repr__(self):
        return "%s %s %s %dm" % (self.id, self.radius, self.coordinates, self.radius)

    def isContainTrackPoint(self, trackPoint):
        tmp = great_circle(self.coordinates.toDegree(), trackPoint.coordinates.toDegree()).m
        #print("%d %d %s %s" % (i, tmp, self.coordinates, trackPoint.coordinates))
        return tmp <= self.radius
