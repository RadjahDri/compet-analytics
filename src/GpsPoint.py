from geopy.distance import great_circle

### CLASSES
class GpsPoint:
    def __init__(self, lat, lon):
        if(type(lat) == type(tuple) or type(lon) == type(tuple)):
            raise Exception("GpsPoint constructor need float degree coordinates values")
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "(%.5f,%.5f)" % (self.lat, self.lon)

    def toDegree(self):
        return (self.lat, self.lon)

    def computeDistance(self, other):
        return great_circle(self.toDegree(), other.toDegree()).m

    @staticmethod
    def fromDegrees(lat, lon):
        return GpsPoint(lat, lon)

    @staticmethod
    def fromDegreesMinutes(lat, lon):
        convLat = convertGpsDegreesMinutesToDegree(lat[0], lat[1], lat[2])
        convLon = convertGpsDegreesMinutesToDegree(lon[0], lon[1], lon[2])
        return GpsPoint(convLat, convLon)

    @staticmethod
    def fromDegreesMinutesSeconds(lat, lon):
        convLat = convertGpsDegreesMinutesSecondsToDegree(lat[0], lat[1], lat[2], lat[3])
        convLon = convertGpsDegreesMinutesSecondsToDegree(lon[0], lon[1], lon[2], lon[3])
        return GpsPoint(convLat, convLon)


### FUNCTIONS
def convertGpsDegreesMinutesToDegree(degrees, minutes, dir):
    if(dir in ["W", "S"]):
        return -(degrees + float(minutes) / 60)
    if(dir in ["N", "E"]):
        return degrees + float(minutes) / 60
    else:
        raise Exception("GPS cardinal point is not valid")


def convertGpsDegreesMinutesSecondsToDegree(degrees, minutes, seconds, dir):
    if(dir in ["W", "S"]):
        return -(degrees + minutes / 60. + seconds / 3600.)
    if(dir in ["N", "E"]):
        return degrees + minutes / 60. + seconds / 3600.
    else:
        raise Exception("GPS cardinal point is not valid")
