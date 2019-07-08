# Reddit Scraping 

This started as a side project but became a presentation for my web scraping and data mining course.
I meant to share this with everyone anyway, but now that it had become a class presentation, I was forced to "finish" it. 
There is always more that can be done, but this is the "final" product for now. 
Modifications were made after the presentation. The commit `2f2126f01cd83ca98f93132f9843be24cdcb802c` is the one that was presented.

The best thing is that you can use this to gather and analyze Reddit posts for yourself! Most things are customizable and a brief description is at the bottom. 

There are two parts to this project: scraping Reddit and analyzing the data that was gathered. 


**Why did I begin this project?**


[Reddit](reddit.com) is a widely used website that I spend a lot of time on. 

There are millions of people around the world that use Reddit. Knowing that got me wondering....

This is some of the stuff I wanted to learn:
* When the most posts were made
* Which subreddits gets the most posts
* Which users post the most often
* If there are many reposts? (same title posted multiple times) 
* What amount of Karma (Reddit points) do users have


## Scraping 

I did the scraping using Reddit [PRAW](https://praw.readthedocs.io/en/latest/) which made it very easy. 

### Output format

I created csv files which held my data. The columns were:

`"Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma"`
(I didnt realize the spaces around Postid until later. Now those have to be there since all the data files will have it that way)


* Iteration Time (home) - The home (PST) time the iteration was done (more about iteration below)
* Iteration Time (utc)  - The UTC time the iteration was done 
* Post Time (utc)       - The UTC time the post was created 
* Subreddit             - The subreddit the post was posted to
* Title                 - The title of the post
* Postid                - The post id
* Author                - The user that made the post
* Total Karma           - The total karma of the user (sum of comment and link karma)

Example entry from `data\popular_short_stream2.csv`:

`05/02/19 23:33:25,05/03/19 06:33:25,05/03/19 06:56:18,"askreddit","Pet owners of reddit what is the stupidest thing your pet has done?",bk5gw0,Jdrstorm,4437`


I had two methods in which I scraped the data, both resulted in the same format. 

### Method 1: Interval

The first method involved scraping posts in regular intervals for a given period of time.

For example, say we want to gather data for 5 hours in 5 minute intervals. That would be 300 minutes in total or 60 intervals. 
So, every 5 minutes, for 60 intervals, it would scrape posts from the given subreddit(s).  Since I do one initial read first, it really does iterations+1. The default way I had it, 250 posts were read every interval or until a post was seen again (by using a tracking post that I called the breakpoint). 


This can be used with more than one subreddit at once just by setting the `subsOfInterest` list. For one subreddit, it is a list with a single string element. 


The duration and interval can be changed. Note however, since this works by reading 250 (default) posts from each subreddit, the timings don't really line up because it eats into the interval wait time. The longer the interval, the closer it comes to the desired total time. The number of intervals is correct though. Using the Stream method (below) is better for more precise timings. This issue may be fixed later. 


Simplified Flow:

```
set end time
set iteration time
find number of iterations
read 25 posts (25 is default)
    record posts
for the number of iterations:
    wait x minutes
        read 250 posts (or until post comes again) (250 is default)
            record posts
```

### Method 2: Stream 


I had originally created this for smaller subreddits where there weren't more than 25 posts every 5 minutes. However, when I used larger subreddits like r/askreddit, I realized that I was missing a ton of posts while it was waiting for the next iteration. In order to fix that, I made smaller intervals until I realized that PRAW supports a way to create a constant stream of posts.


All the data handling is the same as the Interval method except this uses a stream. Currently this only makes a stream for one subreddit (`r/popular` and `r/all` count as subreddits)


Note: Iteration Time (home and utc) in this case is just the time the script was started. 


Simplified Flow:


```
set end time 
open stream to a particular subreddit 
read posts as they come in
    record posts 
    if current time is greater than end time:
        stop
```

### Complications  


At first, I thought this would be pretty easy... It wasn't.


I wanted to run this for long periods of time in order to get lots of data to analyze. I couldn't do it on my laptop since I had to shut it down. So I had to find another way. I ended up running it on a raspberry pi. But with that, came the problem that I couldn't monitor it when I was out and about. So I had to learn to create log files, and I even made a way to post debug stuff to a private subreddit so I could look it when I couldn't access the pi which was only set up on the local network. 



Another issue that came from using the pi was that it uses UTC as the local time but my laptop is in PST. I was very confused about why the times didn't line up, but once I figured it out, I would manually change the time format when running it. I quickly got bored of that and I had to find a way to detect which system I was using. Only issue is that converting from UTC to PST is +7 or 8 hours depending on day light savings and I don't do that automatically as of now. I can probably fix this by using `datetime` a little better. 


I also had to learn to do error checks. In the beginning, it would crash a lot because of exceptions. I realized some of these were due to special characters in post titles. So I began to check for those and just catch it and move on. There were other errors like this for encoding and decoding characters that I had to take care of. As frustrating as it was, it was interesting to see that this was something to keep in mind for long running scripts.


In one of the first runs I had, the csv wouldn't be read correctly. It took me a while to learn that it wasn't something I was doing wrong (for once) but that some titles would have commas in them that would confuse the csv reader. So I began to remove those as I read the titles in. Same thing with double quotes.


## Analyze 


Analyze.py works in three parts: preanalysis, file cleaning if needed, then doing the analysis/making the graphs. 

KNOWN BUG: matplotlib graphs are pickled and stored in the `pickledFigs` directory (if `makePickledFigs` is set to `True`). If the pickledFig exists, analyze.py attempts to use that to show the graph. This was done to make it faster; however, it doesn't show. If the pickledFig is removed, the graph will show.

Also the bokeh plots doesn't show show on rare occasions. Just rerun it and it should be.

When I first started to work with the data, I realized that even if I was the one creating it, it wasn't going to be 100% clean. For instance, with the special characters and other issues discussed above, I would get incomplete rows or rows with an unexpected number of elements (extra commas, etc). In order to fix this, I had to come up with ways to get around it. This let to checking for proper formatting before doing anything.


### PreAnalyze 


I began this preanalysis when I was working with smaller data sets, but I quickly found out that this really helped with large data sets as well. 

This essentially went through and made sure it was in the right format (correct number of elements, no errors, etc). If there were problematic lines, it would print out the line number and the line broken as the csv reader sees it. If this happened, it was not ready to be analyzed.


At first I would manually fix anything that needed fixing


I got tired of inspecting the lines myself, so as any programmer would do...


I automated it


### Cleaning the file


If the PreAnalysis indicated there were errors, I would go though and remove problematic lines. In particular, I ignored lines with `UnicodeEncodeError` in it. This was put in by the scrapers (detailed above) when it came across a `UnicodeEncodeError` which meant that something in the title couldn't be encoded properly. I found that this is the most common  problem with the lines. 

Later on, I found that I could remove this problem by manually encoding the title into ascii and replacing the characters that gave the above issue. I used the `namereplace` option in the string's `encode` method which replaced all the non ascii characters with a `N\{...}` where the `...` is the characters name.

I made it an option to always encode/decode with ascii or allow the `UnicodEncodeError`. Analyze.py cleans both of these things. But by setting `replaceSpecialChar` to `False`, the titles will keep the `N\{...}`. Otherwise, they will be removed via regex and the corresponding postids will be printed out. 


Every now and then, there would be commas in the titles which made reading that row difficult. It would think there are more (or less) elements than I intended. So I also ignore lines that have the incorrect number of elements. This should now be fixed in the scraping and not needed, but I left that check in there anyway.



I could have probably somehow salvaged these lines, but I decided it was easier to ignore them. In the grand scheme of things, it didn't seem like a few titles here and there would make a huge difference for what I wanted to do. 


You can observe how cleaning works by running analyze.py on one of the files in in the `data` directory. 


### Now for the Analysis

Once the data was clean and ready to go, I could finally analyze it. In general, I was interested in counts of various things. I was especially interested in when the post posts were made and what subreddits were the most popular. However, I could make counts for all the columns listed [above](#output-format). 


I read in the csv that I created and used pandas to aggregate the information. I then plotted this data using matplotlib and bokeh. You can see a few of the graphs in the `images` directory.

There is *so* much more I could do. I could try to find correlations between who makes a post and how popular the post gets, or see if particular posters stay in a few subreddits vs post to a lot of them, etc. 

### Complications
For small csvs (scraping from small subreddits or for short periods of time), I saw no issues. However when I scraped from very active subreddits for a lot of time, I would get a lot of data (sometimes over 80,000 lines). When I tried to plot some graphs, it would take a long time to render using matplotlib, if at all. I found that using bokeh solved this issue.


I noticed that this problem happened most when there were may individual counts (many points on the x axis). The Interval time (home and utc) as well as the post time did not seem to have this problem. So I used matplotlib to graph those and used bokeh to plot everything else. I can see the issue coming back for times as well if I got more data.

## Using this project yourself

All you need to do is change the variables in `analyze.py`, `infoInterval.py`, `infoStream.py` to fit your needs. Look for `#### CUSTOMIZE THESE VARIABLES ####` which is where you can change them.

## Final thoughts

All in all, this has been a very fun and insightful project in gathering, using, and learning from real-world data. I would say this is my first "real" data science/data analysis project (even if small) and I had a ton of fun with it. Using data to learn things about it and the world has always been fascinating to me. So, doing something myself and getting results was very exciting. I hope to continue with projects like this in the future. 