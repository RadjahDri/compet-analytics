from Parser.TrackParser.TrackParser import TrackParser
from Track import Track
from GpsPoint import GpsPoint
from TrackPoint import TrackPoint

import datetime
import re

### CONSTANTS
RE_DATE_LINE = re.compile("HFDTEDATE:([0-9]{2})([0-9]{2})([0-9]{2})(?:,[0-9]{2})\n")
RE_DATE_LINE2 = re.compile("HFDTE([0-9]{2})([0-9]{2})([0-9]{2})\n")
RE_PILOT_NAME_LINE = re.compile("HFPLTPILOT:(.*)\n")
RE_PILOT_NAME_LINE2 = re.compile("HFPLTPILOTINCHARGE:(.*)\n")
RE_GLIDER_NAME_LINE = re.compile("HFGTYGLIDERTYPE:(.*)\n")
RE_GLIDER_NAME_LINE2 = re.compile("HFGIDGLIDERID:(.*)\n")
RE_GPS_REFERENCE_LINE = re.compile("HFDTM100GPSDATUM:(.*)\n")
RE_B_LINE = re.compile("B([0-9]{2})([0-9]{2})([0-9]{2})(.{2})(.{5})([N|S])(.{3})(.{5})([W|E])[A|V](-.{4}|.{5})(.{5})")

### CLASSES
class IGCParser(TrackParser):
    def __init__(self, filePath, hourOffset):
        self.filePath = filePath
        self.hourOffset = hourOffset


    def parse(self):
        date = None
        pilotName = ""
        gliderName = ""
        gpsReference = None
        coordinates = {}

        with open(self.filePath) as inputFile:
            line = inputFile.readline()
            while(line):
                if(line.startswith("HFDTEDATE")):
                    match = RE_DATE_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFDTEDATE is not valid")
                    date = datetime.date(int(match.group(3))+2000, int(match.group(2)), int(match.group(1)))

                elif(line.startswith("HFDTE")):
                    match = RE_DATE_LINE2.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFDTE is not valid")
                    date = datetime.date(int(match.group(3))+2000, int(match.group(2)), int(match.group(1)))

                elif(line.startswith("HFPLTPILOT:")):
                    match = RE_PILOT_NAME_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFPLTPILOT is not valid")
                    pilotName = match.group(1)

                elif(line.startswith("HFPLTPILOTINCHARGE:")):
                    match = RE_PILOT_NAME_LINE2.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFPLTPILOTINCHARGE is not valid")
                    pilotName = match.group(1)

                elif(line.startswith("HFGTYGLIDERTYPE:")):
                    match = RE_GLIDER_NAME_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFGIDGLIDERID is not valid")
                    gliderName = match.group(1)

                elif(gliderName == "" and line.startswith("HFGIDGLIDERID:")):
                    match = RE_GLIDER_NAME_LINE2.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFGIDGLIDERID is not valid")
                    gliderName = match.group(1)

                elif(line.startswith("HFDTM100GPSDATUM:")):
                    match = RE_GPS_REFERENCE_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFDTM100GPSDATUM is not valid")
                    gpsReference = match.group(1)

                elif(line.startswith("B")):
                    trackPoint = self.parseBLine(line)
                    coordinates[trackPoint.time] = trackPoint

                line = inputFile.readline()

        track = Track(pilotName, gliderName, date, gpsReference, coordinates)
        return track


    def parseBLine(self, line):
        match = RE_B_LINE.match(line)
        if(not match):
            raise RuntimeError("Parsing failed: B entry is not valid: %s" % line)

        time = datetime.time(int(match.group(1)) + self.hourOffset, int(match.group(2)), int(match.group(3)))
        latDegrees = int(match.group(4))
        latMinutes = float(match.group(5)) / 1000

        lonDegrees = int(match.group(7))
        lonMinutes = float(match.group(8)) / 1000
        alt = int(match.group(11))

        gpsPoint = GpsPoint.fromDegreesMinutes((latDegrees, latMinutes, match.group(6)), (lonDegrees, lonMinutes, match.group(9)))
        trackPoint = TrackPoint(time, gpsPoint, alt)
        return trackPoint
