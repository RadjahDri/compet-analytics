from Parser.TrackParser.IGCParser import IGCParser
from Parser.TaskParser.FSTaskParser import FSTaskParser
from CompetAnalytic import CompetAnalytic

import argparse
import datetime
import os

### CONSTANTS
TIME_FILE_NAME = "time.csv"
ALTITUDE_FILE_NAME = "altitude.csv"

### MAIN
def main(args):
    # Parse task file
    taskParser = FSTaskParser(args.task)
    task = taskParser.parse()
    if(not args.quiet):
        print("[+] Task:\n%s" % task)

    # Init analysis with task
    competAnalytic = CompetAnalytic(task, args.stop)

    # Add competitors tracks to this analysis
    for fileTrackName in os.listdir(args.tracks):
        fileTrackPath = os.path.join(args.tracks, fileTrackName)
        igcParser = IGCParser(fileTrackPath, args.offset)
        track = igcParser.parse()
        if(not args.quiet):
            print("[+] Load track: %s" % track)
        competAnalytic.addCompetitorTrack(track)
        if(not args.quiet):
            print(track)


    tracksStats = competAnalytic.getTurnpointsStats()

    if(args.print):
        print("[+] Statistics")
        for trackStats in tracksStats:
            print("[+] =======")
            print("[+] %s" % trackStats)

    if(args.out):
        timeCsvOutFilePath = os.path.join(args.out, TIME_FILE_NAME)
        altCsvOutFilePath = os.path.join(args.out, ALTITUDE_FILE_NAME)
        competAnalytic.exportTimeToCsv(tracksStats, timeCsvOutFilePath)
        competAnalytic.exportAltitudeToCsv(tracksStats, altCsvOutFilePath)


def argumentParsing():
	parser = argparse.ArgumentParser()

	parser.add_argument("--tracks",
		type=str,
		required=True,
		help="Path to tracks directory")

	parser.add_argument("--task",
		type=str,
		required=True,
		help="Path to task file. Must be FSTask format")

	parser.add_argument("-o", "--out",
		type=str,
		required=False,
		help="Path to output CSV files directory")

	parser.add_argument("-p", "--print",
		action="store_true",
		required=False,
		help="Print competitors results")

	parser.add_argument("-q", "--quiet",
		action="store_true",
		required=False,
		help="Do not print script working information")

	parser.add_argument("--offset",
		type=int,
		required=False,
		default=0,
		help="Hour offset in IGC files")

	parser.add_argument("--stop",
		type=lambda d: datetime.time.fromisoformat(d),
		required=False,
		help="Stop time to this task (Format: hh:mm:ss)")

	return parser.parse_args()


if(__name__ == "__main__"):
	args = argumentParsing()
	exit(main(args))
