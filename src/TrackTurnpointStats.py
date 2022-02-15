### CLASSES
class TrackTurnpointStats:
    def __init__(self, track, nbTurnPoint):
        self.track = track
        self.turnpointsStats = []
        self.nbTurnPoint = nbTurnPoint


    def __repr__(self):
        s = "%s\n" % self.getPilotName()
        s += "%d turnpoints\n" % self.nbTurnPoint
        if(self.isTurnpointPassed(0)):
            ssStats = self.getTurnpointStats(0)
            s += "SS : %s %d\n" % (ssStats.time.strftime("%H:%M:%S"), ssStats.alt)

        if(self.isTurnpointPassed(self.nbTurnPoint - 1)):
            nbPassedTurnpoint = len(self.turnpointsStats) - 2
        else:
            nbPassedTurnpoint = len(self.turnpointsStats) - 1

        for turnpointIdx in range(nbPassedTurnpoint):
            trackPoint = self.getTurnpointStats(turnpointIdx + 1)
            s += "Balise %d: %s %d\n" % (turnpointIdx + 1, trackPoint.time.strftime("%H:%M:%S"), trackPoint.alt)

        if(self.isTurnpointPassed(self.nbTurnPoint - 1)):
            essStats = self.getTurnpointStats(-1)
            s += "ESS : %s %d\n" % (essStats.time.strftime("%H:%M:%S"), essStats.alt)

        return s


    def __lt__(self, other):
        if(len(self.turnpointsStats) != len(other.turnpointsStats)):
            return len(self.turnpointsStats) < len(other.turnpointsStats)
        elif(self.nbTurnPoint == len(self.turnpointsStats)):
            return self.getTurnpointStats(-2).time > other.getTurnpointStats(-2).time
        else:
            return self.getTurnpointStats(-1).time > other.getTurnpointStats(-1).time


    def addTurnpointStats(self, trackPointIdx):
        self.turnpointsStats.append(trackPointIdx)


    def getTurnpointStats(self, turnpointIdx):
        if(turnpointIdx < len(self.turnpointsStats)):
            return self.track.trackPoints[self.turnpointsStats[turnpointIdx]]
        return None


    def isTurnpointPassed(self, turnpointIdx):
        return len(self.turnpointsStats) > turnpointIdx


    def getPilotName(self):
        return self.track.pilotName


    def getGliderName(self):
        return self.track.gliderName


    def exportTimeToCsv(self, ranking):
        csvData = "%s,%s,%d" % (self.getPilotName(), self.getGliderName(), ranking)
        for turnpointIdx in range(self.nbTurnPoint - 1):
            turnpointStats = self.getTurnpointStats(turnpointIdx)
            if(turnpointStats):
                csvData += ",%s" % turnpointStats.time.strftime("%I:%M:%S %p")
            else:
                csvData += ","
        csvData += "\n"

        return csvData


    def exportAltitudeToCsv(self, ranking):
        csvData = "%s,%s,%d" % (self.getPilotName(), self.getGliderName(), ranking)
        for turnpointIdx in range(self.nbTurnPoint):
            turnpointStats = self.getTurnpointStats(turnpointIdx)
            if(turnpointStats):
                csvData += ",%s" % turnpointStats.alt
            else:
                csvData += ","
        csvData += "\n"

        return csvData
