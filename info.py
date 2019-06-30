import os
import sys
import time
import praw
import configR
from praw.models import MoreComments
import datetime
import traceback
if sys.platform == "win32":
    import winsound

# configR is a custom py file to import that holds sensitive info
reddit = praw.Reddit(client_id=configR.client_id,
                     client_secret=configR.client_secret,
                     username=configR.username,
                     password=configR.password,
                     user_agent=configR.user_agent)


def localTimeIsUTC():
    # returns true if local time is utc time
    now = datetime.datetime.now()
    nowutc = datetime.datetime.utcnow()
    nowformated = now.strftime("%A %m/%d/%Y %H:%M")  # example: Thursday 01/24/2019 12:14
    nowutcformated = nowutc.strftime("%A %m/%d/%Y %H:%M")

    return (nowformated == nowutcformated)  # if equal, local time is utc


def waitUntil(timestr, mintoWaitWhileStarting, postXdays):
    # example timestr = "03/31/19 23:48:18"
    # example mintoWaitWhileStarting = 120
    # example postXdays = 5 (post every 5 days)
    waitTime = datetime.datetime.strptime(timestr, "%x %X")

    twelveHoursBefore = (datetime.datetime.strptime(timestr, "%x %X")-datetime.timedelta(hours=12))
    oneMinBefore = (datetime.datetime.strptime(timestr, "%x %X") - datetime.timedelta(minutes=1))
    started = False
    startcounter = 0
    startCounterLim = (postXdays*24*60)/mintoWaitWhileStarting  # post every 5 days
    while not started:
        now = datetime.datetime.now() - datetime.timedelta(hours=7)  # local to home

        if now >= waitTime:
            print("IT HAS STARTED now is %s" % (str(now)))
            started = True
            break

        if not started:
            if twelveHoursBefore < now and now < oneMinBefore:
                time.sleep(30)  # 30 sec
            elif now > oneMinBefore:
                time.sleep(1)
            else:
                if startcounter >= startCounterLim:
                    startcounter = 0
                    # configR.submitSub is a subreddit (probaby private for dev use)
                    reddit.subreddit(configR.submitSub).submit(title='still waiting for info to start', selftext="%s" % (str(now)))
                startcounter = startcounter + 1

                time.sleep(mintoWaitWhileStarting*60)


def numberiterations(totalhours, interval):
    # interval in min
    totalmin = totalhours * 60.0
    return (int(round(totalmin / float(interval))), totalmin)


def initBreakpointDict(subsOfInterest):
    # takes list of subs, returns dict of the last id seen
    # initializes as None
    # this was done since I wanted to allow using more than one sub
    #   When using just one, I could do with one variable to keep track
    breakpointidDict = {}
    for sub in subsOfInterest:
        breakpointidDict[sub] = None
    return breakpointidDict


def cleanTitle(uncleanTitle):
    cleanedTitle = uncleanTitle.replace(",", "")  # so there aren't any comma issues when reading the csv
    cleanedTitle = cleanedTitle.replace("\"", "")  # quote
    # the weird characters are no longer needed now that I endcode/decode
    #   but I'll leave it here since they are common characters
    cleanedTitle = cleanedTitle.replace("’", "")  # weird apostrophe
    cleanedTitle = cleanedTitle.replace("‘", "")  # weird apostrophe
    cleanedTitle = cleanedTitle.replace("“", "")  # weird quote
    cleanedTitle = cleanedTitle.replace("”", "")  # weird quote

    # replace all the other non ascii stuff (emojis, etc)
    cleanedTitle = cleanedTitle.encode("ascii", "namereplace")
    cleanedTitle = cleanedTitle.decode("ascii")

    return cleanedTitle


def info(totalDays, houroffset, interval, outfileName, writeToFile=False):
    errName = "info_error_log.txt"
    localIsUTC = localTimeIsUTC()
    totalpostslookedat = 0
    # utcToPstHoursDiff defined below before calling info(...)
    # subsOfInterest = ["learnpython", "Python", "ucsc"]
    subsOfInterest = ["askreddit", "aww", "showerthoughts"]

    with open(outfileName, "w") as outfile, open(errName, "a") as err:
        seenids = []
        breakpointids = initBreakpointDict(subsOfInterest)

        totalhours = (totaldays * 24.0) + hoursoffset
        iterations, totalmin = numberiterations(totalhours, interval)

        if not localIsUTC:  # tell err file when the run began
            utctime = datetime.datetime.utcnow()
            localtime = datetime.datetime.now()
            hometime = datetime.datetime.now()
            err.write("\n\n - %s (utc) | %s (local) | %s (home)\n" % (utctime, localtime, hometime))
            print("%s - %s (utc) | %s (local) | %s (home)" % (str(0), str(utctime.strftime("%x %X")),
                                                              str(localtime.strftime("%x %X")), str(hometime.strftime("%x %X"))))
        else:
            utctime = datetime.datetime.utcnow()
            localtime = datetime.datetime.now()
            hometime = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)  # convert to local time

            err.write("\n\n - %s (utc) | %s (local) | %s (home)\n" % (utctime, localtime, hometime))
            print("%s - %s (utc) | %s (local) | %s (home)" % (str(0), str(utctime.strftime("%x %X")),
                                                              str(localtime.strftime("%x %X")), str(hometime.strftime("%x %X"))))

        if writeToFile:
            outfile.write("Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma\n")
        for sub in subsOfInterest:
            breakpointid = breakpointids[sub]
            for post in reddit.subreddit(sub).new(limit=25):
                # get the real sub name
                #   if we use "all" or "popular" those arent 'real' subreddits
                #   if we use a 'real' name like 'askreddit' it will be the same
                realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                postid = post.id
                totalpostslookedat = totalpostslookedat + 1
                title = cleanTitle(post.title)

                if breakpointid == None:  # set breakpoint to first post
                    breakpointid = postid
                    breakpointids[sub] = postid

                if postid not in seenids:
                    date = post.created_utc
                    minago = str(int(round(abs(date - time.time()) / 60)))
                    postauth = str(post.author)
                    postauth = str(post.author)
                    if not postauth == "None":  # since converted to string
                        authkarma = str(post.author.link_karma + post.author.comment_karma)
                    else:
                        authkarma = "0"

                    t = "placeholder title for %s" % (str(postid))
                    try:
                        t = title
                        print(" " + str(t))  # print title to console
                    except UnicodeDecodeError:
                        t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                        print("  UnicodeDecodeError on " + str(postid))
                    except:
                        t = "placeholder title;   Error on %s" % (str(postid))
                        print("  something went wrong on  " + str(postid))

                    if writeToFile:
                        try:
                            outfile.write(str(hometime.strftime("%x %X")) + "," + str(utctime.strftime("%x %X")) + ",")
                            writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","
                            outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                          "\"" + "," + postid + "," + postauth + "," + authkarma)
                            outfile.write("\n")
                        except UnicodeEncodeError:
                            outfile.write(",%s,UnicodeEncodeError \n" % (postid))  # for posts with special characters

                    seenids.append(postid)

        postid = ""
        print("total hours: %d (%d min). interval (min): %d. iterations: %d" %
              (totalhours, totalmin, interval, iterations))

        ### iterations ###

        for i in range(1, iterations + 1):
            err.flush()
            if writeToFile:
                outfile.flush()
            try:
                time.sleep(interval * 60)
                # get iteration time
                if not localIsUTC:
                    hometime = str(datetime.datetime.now().strftime("%x %X"))
                    utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                else:
                    hometime = str((datetime.datetime.now() -
                                    datetime.timedelta(hours=utcToPstHoursDiff)).strftime("%x %X"))
                    utctime = str(datetime.datetime.utcnow().strftime("%x %X"))

                for sub in subsOfInterest:
                    postsinSubThisRun = 0
                    breakpointSet = False
                    breakpointid = breakpointids[sub]

                    for post in reddit.subreddit(sub).new(limit=250):
                        realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                        postid = post.id
                        totalpostslookedat = totalpostslookedat + 1
                        postsinSubThisRun = postsinSubThisRun + 1

                        if postid == breakpointid:
                            break  # caught up to the posts we saw

                        if not breakpointSet:  # set the first post seen as the break point
                            breakpointids[sub] = postid
                            breakpointSet = True

                        if postid not in seenids:
                            seenids.append(postid)
                            title = cleanTitle(post.title)

                            postauth == str(post.author)
                            if not postauth == "None":  # since converted to string
                                authkarma = str(post.author.link_karma + post.author.comment_karma)
                            else:
                                authkarma = "0"

                            date = post.created_utc
                            minago = str(int(round(abs(date - time.time()) / 60)))
                            t = "placeholder title for %s" % (str(postid))
                            try:
                                t = title
                                print(" [[%s]] -- %s" % (realsub, t))  # print to console
                            except UnicodeDecodeError:
                                t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                                print("  UnicodeDecodeError on " + str(postid))
                            except:
                                t = "placeholder title;   Error on %s" % (str(postid))
                                print("  something went wrong on  " + str(postid))

                            if writeToFile:
                                try:
                                    outfile.write(hometime + "," + utctime + ",")  # write iterations times
                                    writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","  # post time
                                    outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                                  "\"" + "," + postid + "," + postauth + "," + authkarma)
                                    outfile.write("\n")
                                except UnicodeEncodeError:
                                    outfile.write(",%s,UnicodeEncodeError \n" % (postid))  # for posts with special characters

            except KeyboardInterrupt:
                if not writeToFile:
                    os.remove(outfileName)
                exit()

            except Exception:
                print("ERROR CAUGHT. Check error log.")
                now = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)  # local to home
                reddit.subreddit(configR.submitSub).submit(title="error in info at %s" %
                                                           (str(now)), selftext="ERROR CAUGHT (overall exception catch)\n")
                err.write("ERROR CAUGHT (overall exception catch) at %s\n" % (str(now)))
                err.write(traceback.format_exc())
                err.write("\n")

                if not writeToFile:
                    os.remove(outfileName)
                continue

    if not writeToFile:
        os.remove(outfileName)


writeToFile = True
postToReddit = False

utcToPstHoursDiff = 7
totaldays = 0
hoursoffset = 0.1
interval = 1  # min
outfileName = "testingNewEncoding.csv"

print("writeToFile: %s\npostToReddit: %s\noutfilename: %s" % (str(writeToFile), str(postToReddit), outfileName))
time.sleep(5)

if postToReddit:
    startTime = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> Start: %s' % (str(startTime)), selftext="info")

info(totaldays, hoursoffset, interval, outfileName, writeToFile)
if postToReddit:
    endTime = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> End: %s; \nElapsed: %s' %
                                               (str(endTime), str(endTime-startTime)), selftext="info")

if sys.platform == "win32":
    winsound.Beep(2250, 250)
