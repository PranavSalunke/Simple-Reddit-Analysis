import infoUtil  # has utility functions used in both info Interval and Stream
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


def infoInterval(infoSettings):

    # extract settings
    totaldays = infoSettings["totaldays"]
    hoursoffset = infoSettings["hoursoffset"]
    interval = infoSettings["interval"]
    outfileName = infoSettings["outfileName"]
    subsOfInterest = infoSettings["subsOfInterest"]
    # set default settings, (assumes None)
    # <Default> if not.....
    initialNumPosts = 25 if not infoSettings["initialNumPosts"] else infoSettings["initialNumPosts"]
    numPostsPerInterval = 250 if not infoSettings["numPostsPerInterval"] else infoSettings["numPostsPerInterval"]
    replaceChars = False if not infoSettings["replaceChars"] else infoSettings["replaceChars"]
    writeToFile = False if not infoSettings["writeToFile"] else infoSettings["writeToFile"]
    printToConsole = True if not infoSettings["printToConsole"] else infoSettings["printToConsole"]

    errName = "info_interval_error_log.txt"
    localIsUTC = infoUtil.localTimeIsUTC()
    totalpostslookedat = 0
    # utcToPstHoursDiff defined below before calling info(...)

    with open(outfileName, "w") as outfile, open(errName, "a") as err:
        seenids = []
        breakpointids = initBreakpointDict(subsOfInterest)

        totalhours = (totaldays * 24.0) + hoursoffset
        iterations, totalmin = numberiterations(totalhours, interval)

        utctime = datetime.datetime.utcnow().strftime("%x %X")
        localtime = datetime.datetime.now().strftime("%x %X")
        if not localIsUTC:  # tell err file when the run began
            hometime = datetime.datetime.now().strftime("%x %X")
        else:
            hometime = (datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)).strftime("%x %X")  # convert to local time
        err.write("\n\n - %s (utc) | %s (local) | %s (home)\n" % (utctime, localtime, hometime))
        if printToConsole:
            print("iter[0] - %s (utc) | %s (local) | %s (home)" % (utctime, localtime, hometime))

        if writeToFile:
            outfile.write("Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma\n")
        for sub in subsOfInterest:
            breakpointid = breakpointids[sub]
            for post in reddit.subreddit(sub).new(limit=initialNumPosts):
                # get the real sub name
                #   if we use "all" or "popular" those arent 'real' subreddits
                #   if we use a 'real' name like 'askreddit' it will be the same
                realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                postid = post.id
                totalpostslookedat = totalpostslookedat + 1
                title = infoUtil.cleanTitle(post.title, replaceChars)

                if breakpointid == None:  # set breakpoint to first post
                    breakpointid = postid
                    breakpointids[sub] = postid

                if postid not in seenids:
                    date = post.created_utc
                    minago = str(int(round(abs(date - time.time()) / 60)))
                    postauth = str(post.author)
                    try:  # can be None
                        authkarma = str(post.author.link_karma + post.author.comment_karma)
                    except:
                        authkarma = "0"

                    t = "placeholder title for %s" % (str(postid))
                    try:
                        t = title
                        if printToConsole:
                            print(" [[%s]] -- %s" % (realsub, t))  # print to console
                    except UnicodeDecodeError:
                        t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                        if printToConsole:
                            print("  UnicodeDecodeError on " + str(postid))
                    except:
                        t = "placeholder title;   Error on %s" % (str(postid))
                        if printToConsole:
                            print("  something went wrong on  " + str(postid))

                    if writeToFile:
                        try:
                            outfile.write(hometime + "," + utctime + ",")
                            writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","
                            outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                          "\"" + "," + postid + "," + postauth + "," + authkarma)
                            outfile.write("\n")
                        except UnicodeEncodeError:
                            outfile.write(",%s,UnicodeEncodeError \n" % (postid))  # for posts with special characters

                    seenids.append(postid)

        postid = ""
        if printToConsole:
            print("total hours: %d (%d min). interval (min): %d. iterations: %d" % (totalhours, totalmin, interval, iterations))

        ### iterations ###

        for i in range(1, iterations+1):
            err.flush()
            if writeToFile:
                outfile.flush()
            try:
                if printToConsole:
                    print("== iter[%d] ==" % (i))
                time.sleep(interval * 60)
                # get iteration time
                utctime = datetime.datetime.utcnow().strftime("%x %X")
                if not localIsUTC:
                    hometime = datetime.datetime.now().strftime("%x %X")
                else:
                    hometime = (datetime.datetime.now() -
                                datetime.timedelta(hours=utcToPstHoursDiff)).strftime("%x %X")

                for sub in subsOfInterest:
                    postsinSubThisRun = 0
                    breakpointSet = False
                    breakpointid = breakpointids[sub]

                    for post in reddit.subreddit(sub).new(limit=numPostsPerInterval):
                        realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                        postid = post.id
                        totalpostslookedat = totalpostslookedat + 1
                        postsinSubThisRun = postsinSubThisRun + 1

                        if postid == breakpointid or postid in seenids:
                            # check in seenids incase breakpointid has been removed

                            # if postid == breakpointid:
                            #     print("REACHED BREAKPOINT")
                            # else:
                            #     # will happen if the breakpoint post was deleted
                            #     print("ALREADY IN SEENIDS")

                            break  # caught up to the posts we saw

                        if not breakpointSet:  # set the first post seen as the break point
                            breakpointids[sub] = postid
                            breakpointSet = True

                        if postid not in seenids:
                            seenids.append(postid)
                            title = infoUtil.cleanTitle(post.title, replaceChars)

                            postauth = str(post.author)
                            try:  # can be noen
                                authkarma = str(post.author.link_karma + post.author.comment_karma)
                            except:
                                authkarma = "0"

                            date = post.created_utc
                            minago = str(int(round(abs(date - time.time()) / 60)))
                            t = "placeholder title for %s" % (str(postid))
                            try:
                                t = title
                                if printToConsole:
                                    print(" [[%s]] -- %s" % (realsub, t))  # print to console
                            except UnicodeDecodeError:
                                t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                                if printToConsole:
                                    print("  UnicodeDecodeError on " + str(postid))
                            except:
                                t = "placeholder title;   Error on %s" % (str(postid))
                                if printToConsole:
                                    print("  something went wrong on  " + str(postid))

                            if writeToFile:
                                try:
                                    outfile.write(hometime + "," + utctime + ",")  # write iterations times
                                    writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","  # post time
                                    outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                                  "\"" + "," + postid + "," + postauth + "," + authkarma)
                                    outfile.write("\n")
                                except UnicodeEncodeError:
                                    # should not need now that I encode/decode in clean title
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


#### CUSTOMIZE THESE VARIABLES ####

postToReddit = False
utcToPstHoursDiff = 7  # different when day lights savings is on/off

infoIntervalSettings = {"totaldays": 0,
                        "hoursoffset": 0.1,
                        "interval": 1,  # min
                        "outfileName": "data/infoIntervalDataOut.csv",
                        "subsOfInterest": ["askreddit", "aww", "showerthoughts"],  # list
                        # for the reset, put "None" to use the default
                        "initialNumPosts": None,  # how many posts to read initially
                        "numPostsPerInterval": None,  # how many posts to read every iteration (or until caught up)
                        "replaceChars": True,  # either True/False/None
                        "writeToFile": True,    # either True/False/None
                        "printToConsole": True  # either True/False/None
                        }
#### END CUSTOMIZE THESE VARIABLES ####

if infoIntervalSettings["printToConsole"]:
    for k in infoIntervalSettings.keys():
        print("%s: %s" % (str(k), str(infoIntervalSettings[k])))
    try:
        print("\nWait 5 seconds. Control C if any of these need to be changed!")
        time.sleep(5)  # to control C if any of those settings needs to be fixed
    except KeyboardInterrupt:
        exit()

if postToReddit:
    startTime = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> Start: %s' % (str(startTime)), selftext="info")

started = datetime.datetime.now()
infoInterval(infoIntervalSettings)

if postToReddit:
    endTime = datetime.datetime.now() - datetime.timedelta(hours=utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> End: %s; \nElapsed: %s' %
                                               (str(endTime), str(endTime-startTime)), selftext="info")

if sys.platform == "win32":
    winsound.Beep(2250, 250)
