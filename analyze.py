import datetime
import time
import random
# import pytz
import csv
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os


def cleanUnicodeEncodeError(filename):
    print("cleaning UnicodeEncodeError")
    tempFilename = filename[:filename.find(".csv")] + "__temp.csv"
    os.rename(filename, tempFilename)
    allLines = None
    with open(tempFilename, "r") as oldcsvfile:
        oldreader = csv.reader(oldcsvfile)
        with open(filename, "w", newline='') as newcsvfile:
            newwriter = csv.writer(newcsvfile, delimiter=',')
            header = next(oldreader)
            newwriter.writerow(header)
            for line in oldreader:
                line = [x.strip() for x in line]
                if "UnicodeEncodeError" in line:
                    print(line)
                    continue

                newwriter.writerow(line)

    os.remove(tempFilename)


def preAnalyze(filename):
    print("doing Pre")
    count = 0
    badlines = []
    doAnalyze = True
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        numFields = len(header)
        linenum = 1
        for line in csvreader:
            linenum += 1
            if len(line) != numFields:
                doAnalyze = False
                badlines.append(linenum)
                print("linenum:  "+str(linenum))
                print("linelen: %s/%s" % (str(len(line)), str(numFields)))
                print("line:  ")
                for l in line:
                    print(" ||" + str(l))
                print("----")
                count = count+1
            # print(line)
    print("total bad: %d. lines:  %s" % (count, str(badlines)))
    return doAnalyze


def analyze(filename, field, showAllDates, plottingDate=True):
    print("starting analyze")
    showAllDates = showAllDates

    print("loading data")
    data = pandas.read_csv(filename, encoding="ISO-8859-1")
    data["Iteration Time (home)"] = pandas.to_datetime(data["Iteration Time (home)"], format="%x %X")
    data["Iteration Time (utc)"] = pandas.to_datetime(data["Iteration Time (utc)"], format="%x %X")
    data["Post Time (utc)"] = pandas.to_datetime(data["Post Time (utc)"], format="%x %X")
    print("  loaded data")

    columns = list(data)

    ith = data[field].value_counts(sort=False)
    # ith = data[field].value_counts(sort=True)

    print("building plot")

    fig, ax = plt.subplots()
    ax.set_title("%s | %s vs Counts" % (filename, field))
    if plottingDate:
        ax.plot_date(ith.index, ith.values)

        dateformat = mdates.DateFormatter("%x %I:%M:%S%p")
        ax.xaxis.set_major_formatter(dateformat)
    else:
        ax.scatter(ith.index, ith.values)

    print("  built plot")

    if showAllDates or not plottingDate:
        plt.xticks(ith.index, rotation=10)  # show every date
    else:
        if plottingDate:
            fig.autofmt_xdate()  # format so its not too crowded

    plt.show()


# Fields queried:
#   Iteration Time (home),Iteration Time (utc),Post Time (utc),
#   Subreddit,Title, Postid ,Author,Total Karma

# interested in how it looks for 3 subs: popular (all safe posts), askreddit (large sub), ucsc (smaller but somewhat active sub)
# filename = "small_popular_int.csv"  # small popular using interval
filename = "askreddit_2hInt.csv"  # 2h askreddit int

showAllDates = False
field = "Iteration Time (home)"
# field = "Iteration Time (utc)"
# field = "Post Time (utc)"
# field = "Subreddit"
# field = "Author"
# field = "Title"
# field = " Postid "
plottingDate = "time" in field.lower()

print("for: %s\n" % (filename))


doAnalyze = preAnalyze(filename)
# doAnalyze = True  # when I know the format is fine

if not doAnalyze:
    print("There are some format errors")
    # exit()
    cleanUnicodeEncodeError(filename)

print("preAnalize again")
doAnalyze = preAnalyze(filename)
if not doAnalyze:
    print("There are some format errors even after cleanUnicodeEncodeError")
    exit()

print("\nshowAllDates: %s" % (showAllDates))
print("field: %s" % (field))
print("plotting date: %s\n" % (str(plottingDate)))


analyze(filename, field, showAllDates, plottingDate)
