from TrackTurnpointStats import TrackTurnpointStats

import datetime
import xlsxwriter

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

        # Compute time to each turnpoint to each competitor
        competitionTracksStats = []
        idx = 1
        for track in self.competitorTracks:
            print("[+] Compute track to %s (%d/%d)" % (track.pilotName, idx, len(self.competitorTracks)))
            trackStats = TrackTurnpointStats(track, len(self.task.turnpoints[1:]))

            trackPoint = track.getPointAtTime(self.task.startTime)

            if(trackPoint):
                for turnpointIdx in range(1, len(self.task.turnpoints)):
                    currentBeginSearchTime = trackPoint.time

                    trackPoint = track.searchPointInTurnpoint(self.task.turnpoints[turnpointIdx], currentBeginSearchTime, self.task.endTime)

                    if(not trackPoint):
                        break

                    trackStats.addTurnpointStats(trackPoint)

            competitionTracksStats.append(trackStats)
            idx += 1

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


    def generateTimeXlsSheet(self, competitionTracksStats, xlsFile):
        timeSheet = xlsFile.add_worksheet("Temps")

        # Create formats
        timeFormat = xlsFile.add_format({'num_format': 'hh:mm:ss'})
        timeDeltaFormat = xlsFile.add_format({'num_format': 'mm:ss;-mm:ss'})
        colorScaleFormat = {"type": "3_color_scale", "min_color": "#00a933", "mid_color": "#ffff00", "max_color": "#ff0000"}

        # Generate first row titles
        turnpointTitles = list(map(lambda x: "B%d" % x, range(1, len(self.task.turnpoints) - 4 + 1)))

        row = ["Pilote", "Voile", "Classement", "Départ", "Start"]
        row.extend(turnpointTitles)
        row.extend(["ESS", "Goal", "Durée", "Start"])
        row.extend(turnpointTitles)
        row.extend(["ESS", "Diff moy", "Start"])
        row.extend(turnpointTitles)
        row.extend(["ESS"])
        timeSheet.write_row(0, 0, row)

        # Fill pilots raw data
        ranking = 1
        for competitionTrackStats in competitionTracksStats:
            colIdx = 0
            timeSheet.write_string(ranking, colIdx, competitionTrackStats.getPilotName())
            colIdx += 1
            timeSheet.write_string(ranking, colIdx, competitionTrackStats.getGliderName())
            colIdx += 1
            timeSheet.write_number(ranking, colIdx, ranking)
            colIdx += 1
            timeSheet.write_datetime(ranking, colIdx, self.task.startTime, timeFormat)
            colIdx += 1

            rowData = competitionTrackStats.exportTimeToOds()
            for colIdxOffset in range(len(self.task.turnpoints)):
                if(len(rowData) <= colIdxOffset):
                    break
                timeSheet.write_datetime(ranking, colIdx + colIdxOffset, rowData[colIdxOffset], timeFormat)
            ranking += 1

        # Fill turnpoint time
        colIdxBase = 4 + len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - 1 - len(self.task.turnpoints))
                cell2 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - len(self.task.turnpoints))

                timeSheet.write_formula(rowIdx, colIdx, '=IF(%s=0,"",%s-%s)' % (cell2, cell2, cell1), timeDeltaFormat)

        # Fill difference between turnpoint time and average
        colIdxBase = 3 + 2 * len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - 1 - len(self.task.turnpoints) + 2)
                colName = xlsxwriter.utility.xl_col_to_name(colIdx - 1 - len(self.task.turnpoints) + 2)

                timeSheet.write_formula(rowIdx, colIdx, '=IF(%s="","",%s-AVERAGE(%s$2:%s$%d))' % (cell1, cell1, colName, colName, len(competitionTracksStats)+1), timeDeltaFormat)

        # Fill pilots raw data average and set color scale
        rowIdx += 2
        timeSheet.write_string(rowIdx, 1, "Moyenne")
        colIdxBase = 4
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            timeSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), timeFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)

        # Fill turnpoint time average and set color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 1 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            timeSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), timeFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)

        # Set difference between turnpoint time and average color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 2 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)


    def generateAltitudeXlsSheet(self, competitionTracksStats, xlsFile):
        altSheet = xlsFile.add_worksheet("Alt")

        # Create formats
        intFormat = xlsFile.add_format({'num_format': '##'})
        colorScaleFormat = {"type": "3_color_scale", "min_color": "#ff0000", "mid_color": "#ffff00", "max_color": "#00a933"}

        # Generate first row titles
        turnpointTitles = list(map(lambda x: "B%d" % x, range(1, len(self.task.turnpoints) - 4 + 1)))

        row = ["Pilote", "Voile", "Classement", "Start"]
        row.extend(turnpointTitles)
        row.extend(["ESS", "Goal", "Diff moy", "Start"])
        row.extend(turnpointTitles)
        row.extend(["ESS", "Goal", "Gain"])
        row.extend(turnpointTitles)
        row.extend(["ESS", "Goal", "Diff moy"])
        row.extend(turnpointTitles)
        row.extend(["ESS", "Goal"])
        altSheet.write_row(0, 0, row)

        # Fill pilots raw data
        ranking = 1
        for competitionTrackStats in competitionTracksStats:
            colIdx = 0
            altSheet.write_string(ranking, colIdx, competitionTrackStats.getPilotName())
            colIdx += 1
            altSheet.write_string(ranking, colIdx, competitionTrackStats.getGliderName())
            colIdx += 1
            altSheet.write_number(ranking, colIdx, ranking)
            colIdx += 1

            rowData = competitionTrackStats.exportAltitudeToOds()
            for colIdxOffset in range(len(self.task.turnpoints)):
                if(len(rowData) <= colIdxOffset):
                    break
                altSheet.write_number(ranking, colIdx + colIdxOffset, rowData[colIdxOffset])
            ranking += 1

        # Fill difference between altitude and average
        colIdxBase = 3 + len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - len(self.task.turnpoints))
                colName = xlsxwriter.utility.xl_col_to_name(colIdx - len(self.task.turnpoints))

                altSheet.write_formula(rowIdx, colIdx, '=IF(%s="","",%s-AVERAGE(%s$2:%s$%d))' % (cell1, cell1, colName, colName, len(competitionTracksStats)+1), intFormat)

        # Fill altitude gain in turnpoint
        colIdxBase = 3 + 2 * len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - 2 * len(self.task.turnpoints))
                cell2 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx + 1 - 2 * len(self.task.turnpoints))

                altSheet.write_formula(rowIdx, colIdx, '=IF(%s=0,"",%s-%s)' % (cell2, cell2, cell1), intFormat)

        # Fill difference between altitude gain in turnpoint and average
        colIdxBase = 2 + 3 * len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx + 1 - len(self.task.turnpoints))
                colName = xlsxwriter.utility.xl_col_to_name(colIdx + 1 - len(self.task.turnpoints))

                altSheet.write_formula(rowIdx, colIdx, '=IF(%s="","",%s-AVERAGE(%s$2:%s$%d))' % (cell1, cell1, colName, colName, len(competitionTracksStats)+1), intFormat)



        # Fill pilots raw data average and set color scale
        rowIdx += 2
        altSheet.write_string(rowIdx, 1, "Moyenne")
        colIdxBase = 3
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            altSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), intFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)

        # Set altitude gain in turnpoint color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 1 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)

        # Set difference between turnpoint time and average color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints)
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            altSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), intFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)

        # Set difference between altitude gain in turnpoint and average color scale
        colIdxBase = 2 + 3 * len(self.task.turnpoints)
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)

            altSheet.conditional_format("%s:%s" % (cell1, cell2), colorScaleFormat)


    def exportToXls(self, competitionTracksStats, outputFilePath):
        with xlsxwriter.Workbook(outputFilePath) as xlsFile:
            self.generateTimeXlsSheet(competitionTracksStats, xlsFile)
            self.generateAltitudeXlsSheet(competitionTracksStats, xlsFile)
