from TrackTurnpointStats import TrackTurnpointStats

import datetime

### CONSTANTS
MAX_GLIDER_SPEED_IN_KMH = 100
MAX_GLIDER_SPEED_IN_MS = int(MAX_GLIDER_SPEED_IN_KMH / 3.6)

### CLASSES
class CompetAnalytic:
    def __init__(self, task, stopTime=None):
        if(not task):
            raise ValueError("CompetAnalytic cannot be initialized with empty task")
        self.task = task
        self.competitorTracks = []
        self.stopTime = stopTime


    def addCompetitorTrack(self, track):
        self.competitorTracks.append(track)


    def getTurnpointsStats(self):
        if(not self.competitorTracks):
            raise ValueError("CompetAnalytic cannot generate stats without competitor tracks")

        # Compute time to each turnpoint to each competitor
        competitionTracksStats = []
        for track in self.competitorTracks:
            trackStats = TrackTurnpointStats(track, len(self.task.turnpoints[1:]))

            trackPoint = track.getPointAtTime(self.task.startTime)

            if(trackPoint):
                for turnpointIdx in range(1, len(self.task.turnpoints)):
                    currentBeginSearchTime = trackPoint.time

                    distanceToTurnpoint = trackPoint.coordinates.computeDistance(self.task.turnpoints[turnpointIdx].coordinates) - (self.task.turnpoints[turnpointIdx].radius * 1.005)
                    if(distanceToTurnpoint > 0):
                        minTimeToNextTurnpoint = distanceToTurnpoint // MAX_GLIDER_SPEED_IN_MS
                        currentBeginSearchTime = addTimes(currentBeginSearchTime, minTimeToNextTurnpoint)

                    trackPointIdx = track.searchPointInTurnpoint(self.task.turnpoints[turnpointIdx], currentBeginSearchTime, self.task.endTime)

                    if(trackPointIdx == None):
                        break

                    trackPoint = track.trackPoints[trackPointIdx+1]
                    if(self.stopTime and self.stopTime <= trackPoint.time):
                        break
                    trackStats.addTurnpointStats(trackPointIdx)

            competitionTracksStats.append(trackStats)

        competitionTracksStats.sort(reverse=True)
        return competitionTracksStats


    def exportTimeToCsv(self, competitionTracksStats, outputFilePath=None):
        csvData = "Pilote,Voile,Classement,Start"
        for turnpointIdx in range(1, len(self.task.turnpoints) - 3):
            csvData += ",B%d" % turnpointIdx
        csvData += ",ESS\n"

        ranking = 1
        for competitionTrackStats in competitionTracksStats:
            csvData += competitionTrackStats.exportTimeToCsv(ranking)
            ranking += 1

        if(outputFilePath):
            with open(outputFilePath, "w") as outputFile:
                outputFile.write(csvData)

        return csvData


    def exportAltitudeToCsv(self, competitionTracksStats, outputFilePath=None):
        csvData = "Pilote,Voile,Classement,Start"
        for turnpointIdx in range(1, len(self.task.turnpoints) - 3):
            csvData += ",B%d" % turnpointIdx
        csvData += ",ESS,Goal\n"

        ranking = 1
        for competitionTrackStats in competitionTracksStats:
            csvData += competitionTrackStats.exportAltitudeToCsv(ranking)
            ranking += 1

        if(outputFilePath):
            with open(outputFilePath, "w") as outputFile:
                outputFile.write(csvData)

        return csvData


def addTimes(time, seconds):
    return (datetime.datetime(1,1,1,time.hour, time.minute, time.second) + datetime.timedelta(0, seconds)).time()
