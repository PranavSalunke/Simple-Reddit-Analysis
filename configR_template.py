# a template to the configR.py file
# copy this to a file called configR.py and put in your info
# holds private information, never push or publish this anywhere (configR.py is ignored by git)


### REQUIRED ###
# look at the following links to learn about the client id and secret
# https://praw.readthedocs.io/en/latest/getting_started/authentication.html#oauth 
# https://github.com/reddit-archive/reddit/wiki/OAuth2

client_id="your client id" 
client_secret="your client secret"
username="your reddit user name"
password="the password to your reddit account"
user_agent="presentation"

### OPTIONAL ###

# was used by me to send debug info.
# Not needed to run any of the scripts
# only used if postToReddit is True in info.py and infoStream.py
submitSub = "testing subreddit" 
