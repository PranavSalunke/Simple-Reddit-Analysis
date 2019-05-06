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


def info(totalDays, houroffset, interval, outfileName, writeToFile=False):
    errName = "info_error_log.txt"
    localIsUTC = localTimeIsUTC()
    # subsOfInterest = ["learnpython", "Python", "ucsc"]
    # subsOfInterest = ["learnpython"]
    subsOfInterest = ["askreddit"]
    # subsOfInterest = ["popular"]
    # subsOfInterest = ["ucsc"]

    with open(outfileName, "w") as outfile, open(errName, "a") as err:
        seenids = []
        breakpointid = ""
        postslookedat = 0

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
            hometime = datetime.datetime.now() - datetime.timedelta(hours=7)  # convert to local time

            err.write("\n\n - %s (utc) | %s (local) | %s (home)\n" % (utctime, localtime, hometime))
            print("%s - %s (utc) | %s (local) | %s (home)" % (str(0), str(utctime.strftime("%x %X")),
                                                              str(localtime.strftime("%x %X")), str(hometime.strftime("%x %X"))))

        # if not localIsUTC:
        #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
        #     localtime = str(datetime.datetime.now().strftime("%x %X"))
        #     hometime = str(datetime.datetime.now().strftime("%x %X"))
        #     print("%s - %s (utc) | %s (local) | %s (home)" % (str(0), utctime, localtime, hometime))
        # else:
        #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
        #     localtime = str(datetime.datetime.now().strftime("%x %X"))
        #     hometime = str((datetime.datetime.now() - datetime.timedelta(hours=7)).strftime("%x %X"))
        #     print("%s - %s (utc) | %s (local) | %s (home)" % (str(0), utctime, localtime, hometime))

        if writeToFile:
            outfile.write("Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma\n")
        for sub in subsOfInterest:
            for post in reddit.subreddit(sub).new(limit=25):
                # get the real sub name
                #   if we use "all" or "popular" those arent 'real' subreddits
                #   if we use a 'real' name like 'askreddit' it will be the same
                realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                postid = post.id
                postslookedat = postslookedat + 1
                title = post.title
                title = title.replace(",", "")  # so there aren't any comma issues when reading the csv
                title = title.replace("’", "")  # weird apostrophe

                if postid not in seenids:
                    date = post.created_utc
                    minago = str(int(round(abs(date - time.time()) / 60)))
                    postauth = str(post.author)
                    authkarma = str(post.author.link_karma + post.author.comment_karma)

                    t = "placeholder title for %s" % (str(postid))
                    try:
                        #t = title.encode("cp437", "backslashreplace") + "   [[ " + str(minago) + "m - " + post.id + " ]]"
                        t = title
                        print(" " + str(t))
                    except UnicodeDecodeError:
                        t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                        print("  UnicodeDecodeError on " + str(postid))
                    except:
                        t = "placeholder title;   Error on %s" % (str(postid))
                        print("  something went wrong on  " + str(postid))

                    # if not localIsUTC:
                    #     hometime = str(datetime.datetime.now().strftime("%x %X"))
                    #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                    #     if writeToFile:
                    #         outfile.write(hometime + "," + utctime + ",")
                    #         # outfile.write(str(datetime.datetime.now()) + ",")
                    # else:
                    #     hometime = str((datetime.datetime.now() - datetime.timedelta(hours=7)).strftime("%x %X"))
                    #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                    #     if writeToFile:
                    #         outfile.write(hometime + "," + utctime + ",")
                    #         # outfile.write(str(datetime.datetime.now() - datetime.timedelta(hours=8)) + ",")

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
                    # if sys.platform == "win32":
                    #     winsound.Beep(250, 250)

                if breakpointid == "":
                    breakpointid = postid

        postid = ""
        print("total hours: %d (%d min). interval (min): %d. iterations: %d" %
              (totalhours, totalmin, interval, iterations))
        for i in range(1, iterations + 1):
            err.flush()
            if writeToFile:
                outfile.flush()
            try:
                time.sleep(interval * 60)
                first = None
                postslookedat = 0
                # get iteration time
                if not localIsUTC:
                    hometime = str(datetime.datetime.now().strftime("%x %X"))
                    utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                else:
                    hometime = str((datetime.datetime.now() -
                                    datetime.timedelta(hours=7)).strftime("%x %X"))
                    utctime = str(datetime.datetime.utcnow().strftime("%x %X"))

                for sub in subsOfInterest:
                    for post in reddit.subreddit(sub).new(limit=250):
                        realsub = post.subreddit.display_name.lower()  # this is the one that is put in the csv
                        postid = post.id
                        postslookedat = postslookedat + 1
                        if first is None:
                            first = postid

                        if postid == breakpointid:
                            break  # caught up to the posts we saw

                        if postid not in seenids:
                            title = post.title
                            title = title.replace(",", "")  # so there aren't any comma issues when reading the csv
                            title = title.replace("’", "")  # weird apostrophe
                            postauth = str(post.author)
                            authkarma = str(post.author.link_karma + post.author.comment_karma)
                            # if not localIsUTC: #print out to console
                            #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                            #     localtime = str(datetime.datetime.now().strftime("%x %X"))
                            #     hometime = str(datetime.datetime.now().strftime("%x %X"))
                            #     print("%s - %s (utc) | %s (local) | %s (home)" %
                            #           (str(i), utctime, localtime, hometime))
                            # else:
                            #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                            #     localtime = str(datetime.datetime.now().strftime("%x %X"))
                            #     hometime = str((datetime.datetime.now() -
                            #                     datetime.timedelta(hours=7)).strftime("%x %X"))
                            #     print("%s - %s (utc) | %s (local) | %s (home)" %
                            #           (str(i), utctime, localtime, hometime))

                            date = post.created_utc
                            minago = str(int(round(abs(date - time.time()) / 60)))
                            t = "placeholder title for %s" % (str(postid))
                            try:
                                #t = title.encode("cp437", "backslashreplace")
                                t = title
                                print(" [[%s]] -- %s" % (realsub, t))
                            except UnicodeDecodeError:
                                t = "placeholder title;   UnicodeDecodeError on %s" % (str(postid))
                                print("  UnicodeDecodeError on " + str(postid))
                            except:
                                t = "placeholder title;   Error on %s" % (str(postid))
                                print("  something went wrong on  " + str(postid))
                            # iteration time
                            # if not localIsUTC:
                            #     hometime = str(datetime.datetime.now().strftime("%x %X"))
                            #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                            #     if writeToFile:
                            #         outfile.write(hometime + "," + utctime + ",")
                            #         # outfile.write(str(datetime.datetime.now()) + ",")
                            # else:
                            #     hometime = str((datetime.datetime.now() -
                            #                     datetime.timedelta(hours=7)).strftime("%x %X"))
                            #     utctime = str(datetime.datetime.utcnow().strftime("%x %X"))
                            #     if writeToFile:
                            #         outfile.write(hometime + "," + utctime + ",")

                            if writeToFile:
                                try:
                                    outfile.write(hometime + "," + utctime + ",")  # write iterations times
                                    writedates = str(datetime.datetime.utcfromtimestamp(date).strftime("%x %X")) + ","  # post time
                                    outfile.write(writedates + "\"" + realsub + "\"" + "," + "\"" + str(t) +
                                                  "\"" + "," + postid + "," + postauth + "," + authkarma)
                                    outfile.write("\n")
                                except UnicodeEncodeError:
                                    outfile.write(",%s,UnicodeEncodeError \n" % (postid))  # for posts with special characters

                            seenids.append(postid)
                            # if sys.platform == "win32":
                            #     winsound.Beep(250, 250)

                    breakpointid = first

            except KeyboardInterrupt:
                if not writeToFile:
                    os.remove(outfileName)
                exit()

            except Exception:
                print("ERROR CAUGHT. Check error log.")
                now = datetime.datetime.now() - datetime.timedelta(hours=7)  # local to home
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

totaldays = 0
hoursoffset = 2
interval = 5  # min
outfileName = "testruncsv"

print("writeToFile: %s\npostToReddit: %s\noutfilename: %s" % (str(writeToFile), str(postToReddit), outfileName))
time.sleep(5)

if postToReddit:
    startTime = datetime.datetime.now() - datetime.timedelta(hours=7)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> Start: %s' % (str(startTime)), selftext="info")

info(totaldays, hoursoffset, interval, outfileName, writeToFile)
if postToReddit:
    endTime = datetime.datetime.now() - datetime.timedelta(hours=7)
    reddit.subreddit(configR.submitSub).submit(title='-->>-->> End: %s; \nElapsed: %s' %
                                               (str(endTime), str(endTime-startTime)), selftext="info")

if sys.platform == "win32":
    winsound.Beep(2250, 250)
