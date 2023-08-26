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
        return great_circle(self.coordinates.toDegree(), trackPoint.coordinates.toDegree()).m <= self.radius * 1.005
