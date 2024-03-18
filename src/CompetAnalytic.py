from TrackTurnpointStats import TrackTurnpointStats

import datetime
import xlsxwriter


### CONSTANTS
TIME_SHEET_NAME = "Temps"
ALTITUDE_SHEET_NAME = "Alt"
START_SHEET_NAME = "Start"
TURNPOINT_SHEET_NAME_FMT = "B%d"
ESS_SHEET_NAME = "ESS"
GOAL_SHEET_NAME = "Goal"

GLOBAL_LEFT_PANEL_WIDTH = 3

TIME_RAW_HOUR_LEFT_PANEL_WIDTH = 1
TIME_RAW_HOUR_WIDTH_OFFSET = -2

TIME_DURATION_LEFT_PANEL_WIDTH = 1
TIME_DURATION_WIDTH_OFFSET = -2

TIME_AVERAGE_DURATION_LEFT_PANEL_WIDTH = 1
TIME_DURATION_WIDTH_OFFSET = -2


ALT_RAW_ALT_LEFT_PANEL_WIDTH = 0
ALT_RAW_ALT_WIDTH_OFFSET = -1

ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH = 1
ALT_AVERAGE_ALT_WIDTH_OFFSET = -1

ALT_GAIN_LEFT_PANEL_WIDTH = 0
ALT_GAIN_WIDTH_OFFSET = -1

ALT_AVERAGE_GAIN_LEFT_PANEL_WIDTH = 0
ALT_AVERAGE_GAIN_WIDTH_OFFSET = -1


### GLOBALS
TIME_FORMAT = {'num_format': 'hh:mm:ss'}
TIME_DELTA_FORMAT = {'num_format': 'mm:ss;-mm:ss'}
INT_FORMAT = {'num_format': '##'}
TIME_COLOR_SCALE_FORMAT = {"type": "3_color_scale", "min_color": "#00a933", "mid_color": "#ffff00", "max_color": "#ff0000"}
ALT_COLOR_SCALE_FORMAT = {"type": "3_color_scale", "min_color": "#ff0000", "mid_color": "#ffff00", "max_color": "#00a933"}

### CLASSES
class RefColInfo:
    def __init__(self, targetCol, format, sheetName, bNeedAverage, colorScaleFormat):
        self.targetCol = targetCol
        self.format = format
        self.sheetName = sheetName
        self.bNeedAverage = bNeedAverage
        self.colorScaleFormat = colorScaleFormat


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

            if(self.task.startTime > track.beginTime):
                trackPoint = track.getPointAtTime(self.task.startTime)
            else:
                trackPoint = track.getPointAtTime(track.beginTime)

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
        timeSheet = xlsFile.add_worksheet(TIME_SHEET_NAME)

        timeFormat = xlsFile.add_format(TIME_FORMAT)
        timeDeltaFormat = xlsFile.add_format(TIME_DELTA_FORMAT)

        # Generate first row titles
        turnpointTitles = list(map(lambda x: "B%d" % x, range(1, len(self.task.turnpoints) - 4 + 1)))

        row = ["Pilote", "Voile", "Classement", "Départ", "Start"]
        row.extend(turnpointTitles)
        row.extend(["ESS", "Durée", "Start"])
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
        colIdxBase = 3 + len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 1):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - len(self.task.turnpoints))
                cell2 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx + 1 - len(self.task.turnpoints))

                timeSheet.write_formula(rowIdx, colIdx, '=IF(%s=0,"",%s-%s)' % (cell2, cell2, cell1), timeDeltaFormat)

        # Fill difference between turnpoint time and average
        colIdxBase = 2 + 2 * len(self.task.turnpoints)
        for rowIdx in range(1, len(competitionTracksStats) + 2):
            for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
                cell1 = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx - len(self.task.turnpoints) + 1)
                colName = xlsxwriter.utility.xl_col_to_name(colIdx - len(self.task.turnpoints) + 1)

                timeSheet.write_formula(rowIdx, colIdx, '=IF(%s="","",%s-AVERAGE(%s$2:%s$%d))' % (cell1, cell1, colName, colName, len(competitionTracksStats)+1), timeDeltaFormat)

        # Fill pilots raw data average and set color scale
        rowIdx += 1
        timeSheet.write_string(rowIdx, 1, "Moyenne")
        colIdxBase = 3
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            timeSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), timeFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), TIME_COLOR_SCALE_FORMAT)

        # Fill turnpoint time average and set color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 1 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            timeSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), timeFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), TIME_COLOR_SCALE_FORMAT)

        # Set difference between turnpoint time and average color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 2 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats) , colIdx)
            timeSheet.conditional_format("%s:%s" % (cell1, cell2), TIME_COLOR_SCALE_FORMAT)


    def generateAltitudeXlsSheet(self, competitionTracksStats, xlsFile):
        altSheet = xlsFile.add_worksheet(ALTITUDE_SHEET_NAME)

        intFormat = xlsFile.add_format(INT_FORMAT)

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
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats), colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), ALT_COLOR_SCALE_FORMAT)

        # Set altitude gain in turnpoint color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints) - 1 + 1
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 1):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats), colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), ALT_COLOR_SCALE_FORMAT)

        # Set difference between turnpoint time and average color scale
        colIdxBase = colIdxBase + len(self.task.turnpoints)
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            colName = xlsxwriter.utility.xl_col_to_name(colIdx)
            altSheet.write_formula(rowIdx, colIdx, '=AVERAGE(%s2:%s%d)' % (colName, colName, len(competitionTracksStats)+1), intFormat)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats), colIdx)
            altSheet.conditional_format("%s:%s" % (cell1, cell2), ALT_COLOR_SCALE_FORMAT)

        # Set difference between altitude gain in turnpoint and average color scale
        colIdxBase = 2 + 3 * len(self.task.turnpoints)
        for colIdx in range(colIdxBase, colIdxBase + len(self.task.turnpoints) - 2):
            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(len(competitionTracksStats), colIdx)

            altSheet.conditional_format("%s:%s" % (cell1, cell2), ALT_COLOR_SCALE_FORMAT)


    def generateStartXlsSheet(self, nbCompetitors, nbTurnpoints, xlsFile):
        sheet = xlsFile.add_worksheet(START_SHEET_NAME)

        # Create formats
        timeFormat = xlsFile.add_format(TIME_FORMAT)
        timeDeltaFormat = xlsFile.add_format(TIME_DELTA_FORMAT)
        intFormat = xlsFile.add_format(INT_FORMAT)

        # Set titles
        titles = ["Pilote",	"Voile", "Classement", "Horaire", "Durée", "Diff moy", "Altitude" ,"Diff moy"]

        # Set data from others sheets
        refColInfo = [
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH, timeFormat, TIME_SHEET_NAME, True, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_RAW_HOUR_WIDTH_OFFSET + TIME_DURATION_LEFT_PANEL_WIDTH, timeDeltaFormat, TIME_SHEET_NAME, True, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_RAW_HOUR_WIDTH_OFFSET + TIME_DURATION_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_DURATION_WIDTH_OFFSET + TIME_AVERAGE_DURATION_LEFT_PANEL_WIDTH, timeDeltaFormat, TIME_SHEET_NAME, False, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH, intFormat, ALTITUDE_SHEET_NAME, True, ALT_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET + ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH, intFormat, ALTITUDE_SHEET_NAME, False, ALT_COLOR_SCALE_FORMAT),
        ]
        self.generateDataTurnpointXlsSheet(nbCompetitors, titles, refColInfo, sheet)


    def generateGoalXlsSheet(self, nbCompetitors, nbTurnpoints, xlsFile):
        sheet = xlsFile.add_worksheet(GOAL_SHEET_NAME)

        # Create formats
        timeFormat = xlsFile.add_format(TIME_FORMAT)
        timeDeltaFormat = xlsFile.add_format(TIME_DELTA_FORMAT)
        intFormat = xlsFile.add_format(INT_FORMAT)

        # Set titles
        titles = ["Pilote",	"Voile", "Classement", "Altitude" ,"Diff moy"]

        # Set data from others sheets
        refColInfo = [
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET - 1, intFormat, ALTITUDE_SHEET_NAME, True, ALT_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET + ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_AVERAGE_ALT_WIDTH_OFFSET - 1, intFormat, ALTITUDE_SHEET_NAME, False, ALT_COLOR_SCALE_FORMAT),
        ]
        self.generateDataTurnpointXlsSheet(nbCompetitors, titles, refColInfo, sheet)


    def generateTurnpointXlsSheet(self, nbCompetitors, nbTurnpoints, turnpointIdx, xlsFile, sheetName=None):
        if(not sheetName):
            sheetName = TURNPOINT_SHEET_NAME_FMT % turnpointIdx
        sheet = xlsFile.add_worksheet(sheetName)

        # Create formats
        timeFormat = xlsFile.add_format(TIME_FORMAT)
        timeDeltaFormat = xlsFile.add_format(TIME_DELTA_FORMAT)
        intFormat = xlsFile.add_format(INT_FORMAT)

        # Set titles
        titles = ["Pilote",	"Voile","Classement", "Horaire", "Durée", "Diff moy", "Altitude" ,"Diff moy" ,"Gain" ,"Diff moy"]

        # Set data from others sheets
        refColInfo = [
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH + turnpointIdx, timeFormat, TIME_SHEET_NAME, True, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_RAW_HOUR_WIDTH_OFFSET + TIME_DURATION_LEFT_PANEL_WIDTH + turnpointIdx, timeDeltaFormat, TIME_SHEET_NAME, True, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + TIME_RAW_HOUR_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_RAW_HOUR_WIDTH_OFFSET + TIME_DURATION_LEFT_PANEL_WIDTH + nbTurnpoints + TIME_DURATION_WIDTH_OFFSET + TIME_AVERAGE_DURATION_LEFT_PANEL_WIDTH + turnpointIdx, timeDeltaFormat, TIME_SHEET_NAME, False, TIME_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + turnpointIdx, intFormat, ALTITUDE_SHEET_NAME, True, ALT_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET + ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH + turnpointIdx, intFormat, ALTITUDE_SHEET_NAME, False, ALT_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET + ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_AVERAGE_ALT_WIDTH_OFFSET + ALT_GAIN_LEFT_PANEL_WIDTH + turnpointIdx, intFormat, ALTITUDE_SHEET_NAME, True, ALT_COLOR_SCALE_FORMAT),
            RefColInfo(GLOBAL_LEFT_PANEL_WIDTH + ALT_RAW_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_RAW_ALT_WIDTH_OFFSET + ALT_AVERAGE_ALT_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_AVERAGE_ALT_WIDTH_OFFSET + ALT_GAIN_LEFT_PANEL_WIDTH + nbTurnpoints + ALT_GAIN_WIDTH_OFFSET + ALT_AVERAGE_GAIN_LEFT_PANEL_WIDTH + turnpointIdx, intFormat, ALTITUDE_SHEET_NAME, False, ALT_COLOR_SCALE_FORMAT),
        ]
        self.generateDataTurnpointXlsSheet(nbCompetitors, titles, refColInfo, sheet)


    def generateDataTurnpointXlsSheet(self, nbCompetitors, titles, refColInfo, turnpointSheet):
        for colIdx in range(len(titles)):
            turnpointSheet.write_string(0, colIdx, titles[colIdx])


        for rowIdx in range(1, nbCompetitors + 1):
            for colIdx in range(3):
                cell = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, colIdx)
                turnpointSheet.write_formula(rowIdx, colIdx, '=IF(%s!%s="","",%s!%s' % (TIME_SHEET_NAME, cell, TIME_SHEET_NAME, cell) )

        rowIdx = nbCompetitors + 2
        cell = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, 1)
        turnpointSheet.write_formula(rowIdx, 1, '=IF(%s!%s="","",%s!%s)' % (TIME_SHEET_NAME, cell, TIME_SHEET_NAME, cell))


        colOffset = GLOBAL_LEFT_PANEL_WIDTH
        for colIdx in range(colOffset, colOffset + len(refColInfo)):
            for rowIdx in range(1, nbCompetitors + 1):
                cell = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, refColInfo[colIdx - colOffset].targetCol)
                turnpointSheet.write_formula(rowIdx, colIdx, '=IF(%s!%s="","",%s!%s)' % (refColInfo[colIdx - colOffset].sheetName, cell, refColInfo[colIdx - colOffset].sheetName, cell), refColInfo[colIdx - colOffset].format)

            cell1 = xlsxwriter.utility.xl_rowcol_to_cell(1, colIdx)
            cell2 = xlsxwriter.utility.xl_rowcol_to_cell(nbCompetitors, colIdx)
            turnpointSheet.conditional_format("%s:%s" % (cell1, cell2), refColInfo[colIdx - colOffset].colorScaleFormat)

            if(refColInfo[colIdx - colOffset].bNeedAverage):
                rowIdx = nbCompetitors + 2
                cell = xlsxwriter.utility.xl_rowcol_to_cell(rowIdx, refColInfo[colIdx - colOffset].targetCol)
                turnpointSheet.write_formula(rowIdx, colIdx, '=%s!%s' % (refColInfo[colIdx - colOffset].sheetName, cell), refColInfo[colIdx - colOffset].format)


    def exportToXls(self, competitionTracksStats, outputFilePath):
        with xlsxwriter.Workbook(outputFilePath) as xlsFile:
            self.generateTimeXlsSheet(competitionTracksStats, xlsFile)
            self.generateAltitudeXlsSheet(competitionTracksStats, xlsFile)
            self.generateStartXlsSheet(len(competitionTracksStats), len(self.task.turnpoints), xlsFile)

            for turpointIdx in range(len(self.task.turnpoints) - 3):
                if(turpointIdx == len(self.task.turnpoints) - 4):
                    sheetName = ESS_SHEET_NAME
                else:
                    sheetName = None
                self.generateTurnpointXlsSheet(len(competitionTracksStats), len(self.task.turnpoints), turpointIdx + 1, xlsFile, sheetName)

            self.generateGoalXlsSheet(len(competitionTracksStats), len(self.task.turnpoints), xlsFile)
