### CLASSES
class Task:
    def __init__(self, date, turnpoints, startTime, endTime):
        self.date = date
        self.turnpoints = turnpoints
        self.startTime = startTime
        self.endTime = endTime


    def __repr__(self):
        #s = "Date: %s\n" % self.date.strftime("%d/%m/%Y")
        s = "Start: %s\n" % self.startTime.strftime("%H:%M:%S")
        s += "Close: %s\n" % self.endTime.strftime("%H:%M:%S")
        s += "Takeoff: %s\n" % self.turnpoints[0]
        s += "SS: %s\n" % self.turnpoints[1]
        s += "Turnpoints:\n"
        for turnpoint in self.turnpoints[2:-2]:
            s += "\t%s\n" % turnpoint
        s += "ES: %s\n" % self.turnpoints[-2]
        s += "Goal: %s\n" % self.turnpoints[-1]
        return s
