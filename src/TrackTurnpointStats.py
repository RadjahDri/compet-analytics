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

        if(self.isTurnpointPassed(self.nbTurnPoint - 2)):
            nbPassedTurnpoint = len(self.turnpointsStats) - 3
        else:
            nbPassedTurnpoint = len(self.turnpointsStats) - 2

        for turnpointIdx in range(nbPassedTurnpoint):
            trackPoint = self.getTurnpointStats(turnpointIdx + 1)
            s += "Balise %d: %s %d\n" % (turnpointIdx + 1, trackPoint.time.strftime("%H:%M:%S"), trackPoint.alt)

        if(self.isTurnpointPassed(self.nbTurnPoint - 2)):
            essStats = self.getTurnpointStats(-2)
            s += "ESS : %s %d\n" % (essStats.time.strftime("%H:%M:%S"), essStats.alt)

        if(self.isTurnpointPassed(self.nbTurnPoint - 1)):
            essStats = self.getTurnpointStats(-1)
            s += "Goal : %s %d\n" % (essStats.time.strftime("%H:%M:%S"), essStats.alt)

        return s


    def __lt__(self, other):
        if(len(other.turnpointsStats) == 0):
            return False
        if(len(self.turnpointsStats) == 0):
            return True
        if(len(self.turnpointsStats) != len(other.turnpointsStats)):
            return len(self.turnpointsStats) < len(other.turnpointsStats)
        elif(self.nbTurnPoint == len(self.turnpointsStats)):
            return self.getTurnpointStats(-2).time > other.getTurnpointStats(-2).time
        else:
            return self.getTurnpointStats(-1).time > other.getTurnpointStats(-1).time


    def addTurnpointStats(self, trackPoint):
        self.turnpointsStats.append(trackPoint)


    def getTurnpointStats(self, turnpointIdx):
        if((turnpointIdx >= 0 and turnpointIdx < len(self.turnpointsStats))
            or (turnpointIdx < 0 and abs(turnpointIdx+1) < len(self.turnpointsStats))
        ):
            return self.turnpointsStats[turnpointIdx]
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

    def exportTimeToOds(self):
        row = []
        for turnpointIdx in range(self.nbTurnPoint):
            turnpointStats = self.getTurnpointStats(turnpointIdx)
            if(turnpointStats):
                row.append(turnpointStats.time)
            else:
                break

        return row

    def exportAltitudeToOds(self):
        row = []
        for turnpointIdx in range(self.nbTurnPoint):
            turnpointStats = self.getTurnpointStats(turnpointIdx)
            if(turnpointStats):
                row.append(turnpointStats.alt)
            else:
                break

        return row
