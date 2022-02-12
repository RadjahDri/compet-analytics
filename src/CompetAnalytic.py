from TrackTurnpointStats import TrackTurnpointStats

### CLASSES
class CompetAnalytic:
    def __init__(self, task):
        if(not task):
            raise ValueError("CompetAnalytic cannot be initialized with empty task")
        self.task = task
        self.competitorTracks = []


    def addCompetitorTrack(self, track):
        self.competitorTracks.append(track)


    def getTurnpointsStats(self):
        if(not self.competitorTracks):
            raise ValueError("CompetAnalytic cannot generate stats without competitor tracks")

        competitionTracksStats = []
        for track in self.competitorTracks:
            currentBeginSearchTime = self.task.startTime
            trackStats = TrackTurnpointStats(track, len(self.task.turnpoints[1:-1]))
            for turnpoint in self.task.turnpoints[1:-1]:
                trackPointIdx = track.searchPointInTurnpoint(turnpoint, currentBeginSearchTime, self.task.endTime)
                if(trackPointIdx == None):
                    break
                trackStats.addTurnpointStats(trackPointIdx)
                trackPoint = track.trackPoints[trackPointIdx+1]
                currentBeginSearchTime = trackPoint.time
            competitionTracksStats.append(trackStats)

        competitionTracksStats.sort(reverse=True)
        return competitionTracksStats


    def exportToCsv(self, competitionTracksStats, outputFilePath=None):
        csvData = "Pilote,Classement,Start"
        for turnpointIdx in range(1, len(self.task.turnpoints) - 3):
            csvData += ",B%d" % turnpointIdx
        csvData += ",ESS\n"

        ranking = 1
        for competitionTrackStats in competitionTracksStats:
            csvData += competitionTrackStats.exportToCsv(ranking)
            ranking += 1

        if(outputFilePath):
            with open(outputFilePath, "w") as outputFile:
                outputFile.write(csvData)

        return csvData
