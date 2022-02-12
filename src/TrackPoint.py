### CLASSES
class TrackPoint:
    def __init__(self, time, coordinates, alt):
        self.time = time
        self.coordinates = coordinates
        self.alt = alt

    def __repr__(self):
        return "%s %s %dm" % (self.time.strftime("%H:%m:%S"), self.coordinates, self.alt)
