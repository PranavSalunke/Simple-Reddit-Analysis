import configR
import datetime
import time

# utility methods used in infoInterval and infoStream so that methods don't have to be duplicated


# util:
# - localtimeisutc
# - waituntil
# - clean title


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
