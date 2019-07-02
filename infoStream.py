import os
import sys
import time
import praw
import configR
from praw.models import MoreComments
import prawcore
import datetime
import traceback
if sys.platform == "win32":
    import winsound

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


def cleanTitle(uncleanTitle, replaceChars=False):
    cleanedTitle = uncleanTitle.replace(",", "")  # so there aren't any comma issues when reading the csv
    cleanedTitle = cleanedTitle.replace("\"", "")  # quote
    # the weird characters are no longer needed now that I endcode/decode
    #   but I'll leave it here since they are common characters
    cleanedTitle = cleanedTitle.replace("’", "")  # weird apostrophe
    cleanedTitle = cleanedTitle.replace("‘", "")  # weird apostrophe
    cleanedTitle = cleanedTitle.replace("“", "")  # weird quote
    cleanedTitle = cleanedTitle.replace("”", "")  # weird quote

    # replace all the other non ascii stuff (emojis, etc)
    if replaceChars:
        cleanedTitle = cleanedTitle.encode("ascii", "namereplace")
        cleanedTitle = cleanedTitle.decode("ascii")

    return cleanedTitle


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
        now = datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)  # local to home

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
                    reddit.subreddit(configR.submitSub).submit(title='still waiting for info to start', selftext="%s" % (str(now)))
                startcounter = startcounter + 1

                time.sleep(mintoWaitWhileStarting*60)


def info(totalDays, houroffset, outfileName, replaceChars=False, writeToFile=False):
    streamStartTime = datetime.datetime.now()
    lastFileFlush = datetime.datetime.now()
    errName = "info_error_log.txt"
    localIsUTC = localTimeIsUTC()
    subOfInterest = "popular"

    with open(outfileName, "w") as outfile, open(errName, "a") as err:
        seenids = []
        breakpointid = ""
        postslookedat = 0

        totalhours = (totaldays * 24.0) + hoursoffset

        # NOTE: for the streamed data, Iteration Time (home) and Iteration Time (utc) is the time the stream was started

        utctime = datetime.datetime.utcnow().strftime("%x %X")
        localtime = datetime.datetime.now().strftime("%x %X")
        if not localIsUTC:
            hometime = datetime.datetime.now().strftime("%x %X")
        else:
            hometime = (datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)).strftime("%x %X")  # convert to local time
        # tell err file when the run began
        err.write("\n\n - %s (utc) | %s (local) | %s (home)\n" % (utctime, localtime, hometime))
        print("%s (utc) | %s (local) | %s (home)" % (utctime, localtime, hometime))

        if writeToFile:
            outfile.write("Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma\n")

        exceptCount = 0
        try:
            # make an open stream
            for post in reddit.subreddit(subOfInterest).stream.submissions():
                realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                postid = post.id
                postslookedat = postslookedat + 1
                title = cleanTitle(post.title, replaceChars)

                # can assume post has not been seen before
                date = post.created_utc
                postauth = str(post.author)
                authkarma = str(post.author.link_karma + post.author.comment_karma)

                t = "placeholder title for %s" % (str(postid))
                try:
                    t = title
                    print(" [[%s]] -- %s" % (realsub, t))
                except UnicodeDecodeError:
                    t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                    print("  UnicodeDecodeError on " + str(postid))
                except:
                    t = "placeholder title;   Error on %s" % (str(postid))
                    print("  something went wrong on  " + str(postid))

                if writeToFile:
                    try:
                        outfile.write(hometime + "," + utctime + ",")
                        writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","
                        outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                      "\"" + "," + postid + "," + postauth + "," + authkarma)
                        outfile.write("\n")
                    except UnicodeEncodeError:
                        # should not need now that I encode/decode in clean title
                        outfile.write(",%s,UnicodeEncodeError \n" % (postid))  # for posts with special characters

                nowtime = datetime.datetime.now()
                # flush file buffers every 1 min
                if nowtime > lastFileFlush + datetime.timedelta(minutes=1):
                    lastFileFlush = nowtime
                    err.flush()
                    if writeToFile:
                        outfile.flush()

                # check if it has been X hours since starting
                if nowtime > streamStartTime + datetime.timedelta(hours=totalhours):
                    print("\nIt has been %s hours. Ending stream listen" % (str(totalhours)))
                    # flush the file buffers
                    err.flush()
                    if writeToFile:
                        outfile.flush()
                    break
        except KeyboardInterrupt:
            err.flush()
            if writeToFile:
                outfile.flush()
            exit()
        except prawcore.exceptions.NotFound:
            exceptCount += 1
            if not localIsUTC:
                errTime = str(datetime.datetime.now().strftime("%x %X"))
            else:
                errTime = str((datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)).strftime("%x %X"))
            print("Prawcore notfound ERROR CAUGHT. Check error log.")

            err.write("Prawcore notfound ERROR CAUGHT at %s\n" % (str(errTime)))
            err.write(traceback.format_exc())
            err.write("\n")

            err.flush()
            if writeToFile:
                outfile.flush()

            if exceptCount > 5:
                # too many attempts
                print("too may attempts; exiting")
                err.write("too may attempts; exiting\n")
                exit()
        except:
            print("SOME ERROR :((")
            exceptCount += 1
            if not localIsUTC:
                errTime = str(datetime.datetime.now().strftime("%x %X"))
            else:
                errTime = str((datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)).strftime("%x %X"))

            print("ERROR CAUGHT. Check error log.")
            err.write("ERROR CAUGHT (overall exception catch) at %s\n" % (str(errTime)))
            err.write(traceback.format_exc())
            err.write("\n")

            err.flush()
            if writeToFile:
                outfile.flush()

            if exceptCount > 5:
                # too many attempts
                print("too may attempts; exiting")
                err.write("too may attempts; exiting\n")
                exit()

        else:
            # no error
            exceptCount = 0

    if not writeToFile:
        os.remove(outfileName)


replaceChars = True
writeToFile = True
postToReddit = False

# note for some reason a stream for popular breaks (might be too fast?)
utcToPstHoursDiff = 7
totaldays = 0
hoursoffset = 0.1  # 6 min
outfileName = "test_Stream_replace.csv"

print("writeToFile: %s\npostToReddit: %s\noutfilename: %s" % (str(writeToFile), str(postToReddit), outfileName))
time.sleep(5)

if postToReddit:
    startTime = datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> Start: %s' % (str(startTime)), selftext="info")

info(totaldays, hoursoffset, outfileName, replaceChars, writeToFile)

if postToReddit:
    endTime = datetime.datetime.now() - datetime.timedelta(utcToPstHoursDiff)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> End: %s; \nElapsed: %s' %
                                               (str(endTime), str(endTime-startTime)), selftext="info")

if sys.platform == "win32":
    winsound.Beep(2250, 250)
