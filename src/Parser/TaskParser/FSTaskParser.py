from Parser.TaskParser.TaskParser import TaskParser
from GpsPoint import GpsPoint
from TaskPoint import TaskPoint
from Task import Task

import xml.etree.ElementTree as XML
import datetime
import re

### CONSTANTS
RE_DATETIME_STR = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}):([0-9]{2}):([0-9]{2})\+[0-9]{2}:[0-9]{2}")

### CLASSES
class FSTaskParser(TaskParser):
    def parse(self):
        date = None
        takeoff = None
        ss = None
        turnpoints = []
        es = None
        goal = None
        startTime = None
        endTime = None

        tree = XML.parse(self.filePath)
        root = tree.getroot()
        fsTaskDefinition = root.find("FsTaskDefinition")
        fsTurnpoints = fsTaskDefinition.findall("FsTurnpoint")

        turnpoints = list(map(self.parseTurnPoint, fsTurnpoints))

        fsStartGate = fsTaskDefinition.find("FsStartGate")
        openingStr = fsStartGate.get("open")

        match = RE_DATETIME_STR.match(openingStr)
        if(not match):
            raise RuntimeError("Parsing failed: FsStartGate['open'] is not valid: %s" % openingStr)
        startTime = datetime.time(int(match.group(1)), int(match.group(2)), int(match.group(3)))

        fsTaskState = root.find("FsTaskState")
        closeTimeStr = fsTaskState.get("stop_time")

        match = RE_DATETIME_STR.match(closeTimeStr)
        if(not match):
            raise RuntimeError("Parsing failed: fsTaskState['stop_time'] is not valid: %s" % closeTimeStr)
        endTime = datetime.time(int(match.group(1)), int(match.group(2)), int(match.group(3)))


        task = Task(date, turnpoints, startTime, endTime)
        return task


    def parseTurnPoint(self, fsTurnpoint):
        id = fsTurnpoint.get("id")
        lat = float(fsTurnpoint.get("lat"))
        lon = float(fsTurnpoint.get("lon"))
        radius = int(fsTurnpoint.get("radius"))

        gpsPoint = GpsPoint(lat, lon)
        return TaskPoint(id, gpsPoint, radius)
