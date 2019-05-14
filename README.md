# Reddit Scraping 

This started as a side project but became a presentation for my web scraping and data mining course.
I mean to share this with everyone anyway, but now that it had become a class presentation, I was forced to "finish" it. 
There is always more that can be done, but this is the "final" product for now.

There are two parts to this project: scraping Reddit and analyzing the data that was gathered. 


**Why did I begin this project?**


[Reddit](reddit.com) is a widely used website that I spend a lot of time on. 

There are millions of people worldwide that use Reddit all through out the day. I began to have a couple questions.

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

`Iteration Time (home),Iteration Time (utc),Post Time (utc),Subreddit,Title, Postid ,Author,Total Karma`


* Iteration Time (home) - The home time the iteration was done (home is PST time) (more about iteration below)
* Iteration Time (utc)  - The UTC time the iteration was done 
* Post Time (utc)       - The UTC time the post was created 
* Subreddit             - The subreddit the post was posted to
* Title                 - The title of the post
* Postid                - The post id
* Author                - The user that made the post
* Total Karma           - The total karma of the user (sum of comment and post karma)

I had two methods in which I scraped the data, both outputted the same data in the same format. 

### Method 1: Interval

The first method involved scraping posts in regular intervals for a given period of time. 

For example, say we want to gather data for 5 hours in 5 minute intervals. That would be 300 minutes in total or 60 intervals. 
So, every 5 minutes, for 60 intervals, it would scrape posts from a given subreddit. The way I had it was it would read 25 posts every interval or until a post came up again. 


Simplified Flow:

```
set end time
set iteration time
find number of iterations
read 250 posts
    record posts
for the number of iterations:
    wait x minutes
        read 25 posts (or until post comes again)
            record posts
```

### Method 2: Stream 


I had originally created this for smaller subreddits where there weren't more than 25 posts every 5 minutes. However, when I used larger subreddits like r/askreddit, I realized that I was missing a ton of posts while it was waiting for the next iteration. In order to fix that, I made smaller itervals until I realized that PRAW supports a way to create a constant stream of posts.


All the data handling is the same as the Interval method except this uses a stream.


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


At first, I though this would be pretty easy... It wasn't. I wanted to run this for long periods of time in order to get lots of data to analyze. I couldn't do it on my laptop since I had to shut it down. So, I needed to run it on a raspberry pi. But with that, came the problem that I couldn't monitor it when I was out and about. So I had to learn to create log files, and I even made a way to post debug stuff to a private subreddit so I could look it when I couldn't access the pi. 



Another issue that came from using the pi was that it uses UTC as the local time but my laptop is in PST. I was very confused about why the times didn't line up, but once I figured it out, I would manually change the time format when running it. I quickly got bored of that and I had to find a way to detect which system I was using. 


I also had to learn to do error checks. In the beginning, it would crash a lot because of exceptions. I realized some of these were due to special characters in post titles. So I began to check for those and just catch it and move on. There were other errors like this for encoding and decoding characters that I had to take care of. As frustrating as it was, it was interesting to see that this was something to keep in mind.


In one of the first runs I had, the csv wouldn't be read correctly. It took me a while to learn that it wasn't something I was doing wrong (for once) but that some titles would have commas in them that would confuse the csv reader. So I began to remove those as I read the titles in. Same thing with double quotes.


## Analyze 


### Complications


## Final thoughts

All in all, this has been a very fun and insightful project in gathering, using, and learning from real-world data. I would say this is my first "real" data science project (even if small) and I had a ton of fun with it. Using data to learn things about it and the world has always been fascinating to me. So, doing something myself and getting results was very exciting. I hope to continue with projects like this in the future. 