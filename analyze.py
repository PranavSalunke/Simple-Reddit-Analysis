import datetime
import time
import random
import csv
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import pickle
from bokeh.plotting import figure, output_file, show, save
import re


def createPickledName(filename, field):
    _, basefilename = os.path.split(filename)
    basefilename = basefilename[:basefilename.rfind(".")]  # ignore extention
    pickleName = "pickledFigs/" + basefilename + "__" + field + ".pickle"
    return pickleName


def rmSpecialCharName(line):
    # line is supposed to be the list created when reading with the csv.reader as is done in cleanFile
    # returns a new list with the escape sequence removed
    oldtitle = line[4]
    title = line[4]
    title = title.replace("\\N", "")  # because using the pattern "\\N\{[A-Z] +\}" was giving issues due to the escape N(\N)
    pattern = "\{[A-Z- 0-9]+\}"
    title = re.sub(pattern, "", title)
    if not title.strip():  # empty after removing special chars
        title = "PLACEHOLDER TITLE FROM ANALYZE.PY: title empty after removing special characters."
    line[4] = title

    removed = oldtitle != title

    return line, removed


def cleanFile(filename, replaceSpecialChar):
    print("cleaning %s" % (filename))

    tempFilename = filename[:filename.find(".csv")] + "__temp.csv"
    os.rename(filename, tempFilename)
    allLines = None
    with open(tempFilename, "r", encoding="ISO-8859-1") as oldcsvfile:
        oldreader = csv.reader(oldcsvfile)
        with open(filename, "w", newline='', encoding="ISO-8859-1") as newcsvfile:
            newwriter = csv.writer(newcsvfile, delimiter=',')
            header = next(oldreader)
            numFields = len(header)
            newwriter.writerow(header)
            for line in oldreader:
                line = [x.strip() for x in line]

                if replaceSpecialChar:
                    line, replaced = rmSpecialCharName(line)
                    if replaced:
                        print("removed special characters from post with id: %s" % (line[5]))

                if "UnicodeEncodeError" in line:
                    print("remove UnicodeEncodeError: %s" % (line))
                    continue

                if len(line) != numFields:
                    print("remove incorrect line len: %s" % (line))
                    continue

                newwriter.writerow(line)

    os.remove(tempFilename)


def preAnalyze(filename):
    print("doing Preanalysis")
    count = 0
    badlines = []
    doAnalyze = True
    with open(filename, "r", encoding="ISO-8859-1") as csvfile:
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


def analyze(filename, field, showAllDates, makePickledFigs, saveHTML):
    print("starting analyze")
    plottingDate = "time" in field.lower()

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
    startBuild = datetime.datetime.now()

    if plottingDate:
        pickleName = createPickledName(filename, field)
        if not os.path.exists(pickleName):
            # matplotlib is verrry slow for huge data sets
            # but I know how to show date using matplotlib (and I know this shows ok using plt)
            fig, ax = plt.subplots()
            ax.set_title("%s\n%s vs Counts" % (filename, field))
            ax.plot_date(ith.index, ith.values)

            dateformat = mdates.DateFormatter("%x %I:%M:%S%p")
            ax.xaxis.set_major_formatter(dateformat)

            if showAllDates:
                plt.xticks(ith.index, rotation=10)  # show every date
            else:
                fig.autofmt_xdate()  # format so its not too crowded
            print("  built plot")
            print("    Build took: %s" % (str(datetime.datetime.now() - startBuild)))
            plt.show()

            if makePickledFigs:
                print("pickling fig")
                pickle.dump(fig, open(pickleName, "wb"))
        else:  # just load the pickledfig (also saves on process time)
            print("loading pickledfig took: %s" % (str(datetime.datetime.now() - startBuild)))
            # load the pickled fig (assumes the data file is unchanged so the plots are unchanged)
            fig = pickle.load(open(pickleName, 'rb'))
            plt.show()

    else:
        # bokeh is better for large data sets, not sure how sto do time on it so use matplotlib
        if field == "Total Karma":
            plot = figure(plot_width=800, plot_height=500, title="%s -- %s vs Counts" % (filename, field))
        else:
            # categorical data
            plot = figure(x_range=list(ith.index), plot_width=800, plot_height=500, title="%s -- %s vs Counts" % (filename, field))

        plot.circle(ith.index, ith.values, size=8, color="blue", alpha=0.8)
        _, basefilename = os.path.split(filename)
        basefilename = basefilename[:basefilename.rfind(".")]  # ignore extention
        htmlfilename = "analyze_%s__%s.html" % (basefilename, field)
        output_file(htmlfilename)
        print("  built plot")
        print("    Build took: %s" % (str(datetime.datetime.now() - startBuild)))
        print("NOTE: could take a few moments to load. If it does not, set saveHTML to True so it is not automatically removed")
        show(plot)

        time.sleep(1.5)  # let it load or the graph wont show
        if not saveHTML:  # just show it, dont save the html files
            try:
                os.remove(htmlfilename)  # remove the html file
                print("deleted plot html file %s" % (htmlfilename))
            except PermissionError:  # still loading
                print("could not remove %s. Trying again in 1 second" % (htmlfilename))
                time.sleep(1)  # wait another second
                try:
                    os.remove(htmlfilename)  # try to remove the html file again
                    print("deleted plot html file %s (on second try)" % (htmlfilename))
                except:
                    print("could not remove %s on second try; not attempting again" % (htmlfilename))


def doOneField(filename, field, replaceSpecialChar, showAllDates, makePickledFigs, saveHTML):
    doAnalyze = preAnalyze(filename)

    if not doAnalyze or replaceSpecialChar:
        print("There are some format errors and/or replacing special chars")
        cleanFile(filename, replaceSpecialChar)

    print("\npreAnalize again")
    doAnalyze = preAnalyze(filename)
    if not doAnalyze:
        print("There are some format errors even after cleaning. Please fix manually")
        exit()

    analyze(filename, field, showAllDates, makePickledFigs, saveHTML)


def doAllFields(filename, replaceSpecialChar, showAllDates, makePickledFigs, saveHTML):
    fields = ["Iteration Time (home)", "Iteration Time (utc)", "Post Time (utc)", "Subreddit", "Title", "Author", "Total Karma"]
    # not plotting postid since that is unique anyway

    doAnalyze = preAnalyze(filename)

    if not doAnalyze or replaceSpecialChar:
        print("There are some format errors and/or replacing special chars")
        cleanFile(filename, replaceSpecialChar)

    print("\npreAnalize again")
    doAnalyze = preAnalyze(filename)
    if not doAnalyze:
        print("There are some format errors even after cleaning. Please fix manually")
        exit()

    for f in fields:
        if "stream" in filename.lower() and "iteration" in f.lower():
            print("=== " + f.upper() + " === ")
            print("skipping since they are all one time")
            continue  # skip the iteration time for streams since they are all one time

        print(" === " + f.upper() + " === ")
        analyze(filename, f, showAllDates, makePickledFigs, saveHTML)
        print()


#### CUSTOMIZE THESE VARIABLES ####

filename = "data/file.csv"  # created by infoInterval.py or infoStream.py
showAllDates = False  # show all the collected date data if True, if False, let matplotlib create the scale
replaceSpecialChar = True
makePickledFigs = True
saveHTML = False

# Fields queried: (field can be any of these)
#   Iteration Time (home),Iteration Time (utc),Post Time (utc),
#   Subreddit,Title, Postid ,Author,Total Karma

field = "Iteration Time (home)"
# field = "Iteration Time (utc)"
# field = "Post Time (utc)"
# field = "Subreddit"
# field = "Author"
# field = "Title"
# field = "Total Karma"
# field = " Postid " # needs to have the spaces

#### END CUSTOMIZE THESE VARIABLES ####

# doOneField(filename, field, replaceSpecialChar, showAllDates, makePickledFigs, saveHTML)
doAllFields(filename, replaceSpecialChar, showAllDates, makePickledFigs, saveHTML)
