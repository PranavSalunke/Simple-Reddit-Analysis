import datetime
import time
import random
# import pytz
import csv
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import pickle
from bokeh.plotting import figure, output_file, show, save


def creeatePickledName(filename, field):
    slashPos = filename.find("/")
    slashPos = slashPos if slashPos != -1 else 0  # if no slash, start at beggining
    dotPos = filename.find(".")
    pickleName = "pickledFigs/" + filename[slashPos:dotPos] + "__" + field + ".pickle"
    return pickleName


def createPickledFig(pickleName, fig):
    pickle.dump(fig, open(pickleName, "wb"))


def loadPickledFig(figname):
    fig = pickle.load(open(figname, 'rb'))
    plt.show()


def cleanFile(filename):
    print("cleaning UnicodeEncodeError")
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


def analyze(filename, field, showAllDates, plottingDate=True, saveHTML=False):
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
    startBuild = datetime.datetime.now()

    fig, ax = plt.subplots()

    if plottingDate:
        # matplotlib is verry slow for huge data sets
        # but i knwo how to show date
        ax.set_title("%s\n%s vs Counts" % (filename, field))
        ax.plot_date(ith.index, ith.values)

        dateformat = mdates.DateFormatter("%x %I:%M:%S%p")
        ax.xaxis.set_major_formatter(dateformat)

        if showAllDates:
            plt.xticks(ith.index, rotation=10)  # show every date
        else:
            fig.autofmt_xdate()  # format so its not too crowded

        pn = creeatePickledName(filename, field)
        if not os.path.exists(pn):
            print("pickling fig")
            createPickledFig(pn, fig)

        plt.show()
    else:
        # bokeh is better for large data sets, not sure how to do time on it so use matplotlib
        if field == "Total Karma":
            plot = figure(plot_width=800, plot_height=500, title="%s -- %s vs Counts" % (filename, field))
        else:
            # categorical data
            plot = figure(x_range=list(ith.index), plot_width=800, plot_height=500, title="%s -- %s vs Counts" % (filename, field))

        plot.circle(ith.index, ith.values, size=8, color="blue", alpha=0.8)
        basefilename = filename[:filename.rfind(".")]  # ignore extention
        htmlfilename = "analyze_%s_%s.html" % (basefilename, field)
        output_file(htmlfilename)
        show(plot)
        time.sleep(0.3)  # let the rest load
        if not saveHTML:  # just show it, dont save the html files
            try:
                os.remove(htmlfilename)  # remove the html file
            except PermissionError:  # still loading
                print("wait more")
                time.sleep(0.5)  # wait another half second
                os.remove(htmlfilename)  # try to remove the html file again

    print("  built plot")
    print("    Build took: %s" % (str(datetime.datetime.now() - startBuild)))


# Fields queried:
#   Iteration Time (home),Iteration Time (utc),Post Time (utc),
#   Subreddit,Title, Postid ,Author,Total Karma

# interested in how it looks for 3 subs: popular (all safe posts), askreddit (large sub), ucsc (smaller but somewhat active sub)

# filename = "small_popular_int.csv"  # small popular using interval
# filename = "askreddit_2hInt.csv"  # 2h askreddit int
# filename = "30min_popular_stream.csv"
# filename = "30min_popular_stream2.csv"
# filename = "30min_popular_5minInt.csv"

# long runs
# filename = "data/ucsc_2day12hour_interval5min.csv"
# filename = "data/ucsc_2day12hour_stream.csv"

# filename = "data/askreddit_2day12hour_interval5min.csv"
# filename = "data/askreddit_2day12hour_stream.csv"

# filename = "data/Popular_2day12hour_interval5min.csv"
# filename = "data/popular_short_stream2.csv"


filename = "testingNewBreakpoint3_b.csv"

fields = ["Iteration Time (home)", "Iteration Time (utc)", "Post Time (utc)", "Subreddit", "Title", "Author", "Total Karma"]
# not plotting postid since that is unique anyway

field = "Iteration Time (home)"
# field = "Iteration Time (utc)"
# field = "Post Time (utc)"
# field = "Subreddit"
# field = "Author"
# field = "Title"
# field = "Total Karma"
# field = " Postid "
plottingDate = "time" in field.lower()
showAllDates = False  # show all the collected date data if True, if False, let matplotlib create the scale

print("for: %s\n" % (filename))


doAnalyze = preAnalyze(filename)
# doAnalyze = True  # when I know the format is fine

if not doAnalyze:
    print("There are some format errors")
    # exit()
    print("MAKE SURE TO SAVE A FILE WITH THE ERROR TO SHOW")
    cleanFile(filename)

print("preAnalize again")
doAnalyze = preAnalyze(filename)
if not doAnalyze:
    print("There are some format errors even after cleanUnicodeEncodeError")
    exit()

print("\nshowAllDates: %s" % (showAllDates))
print("field: %s" % (field))
print("plotting date: %s\n" % (str(plottingDate)))

# load pickled figure (matplotlib)
# pickedFigName = creeatePickledName("30min_popular_5minInt.csv", "Iteration Time (home)")
# loadPickledFig(pickedFigName)


# analyze(filename, field, showAllDates, plottingDate)
for f in fields:
    if "stream" in filename and "Iteration" in f:
        print("SKIPPING === " + f.upper() + " === ")
        continue  # skip the iteration time for streams since they are all one time

    print(" === " + f.upper() + " === ")
    p = "time" in f.lower()
    analyze(filename, f, showAllDates, p)
    print()
