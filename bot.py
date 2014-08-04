"""
**someredditusername by /u/you**
*Inspired by /u/person on /r/RequestABot*

This bot just finds comments in a list
of subreddits with the word "gist" in the
body and replies with a small comment.
"""

import praw
import bmemcached
import time
import os     # for all bots

from __future__ import print_function  # to print to stderr
from requests import HTTPError        # to escape ban errors
import sys                            # for all errors

import re                             # if you want to use regex
import textwrap                       # if you want to post multiline comments
from pyteaser import Summarize

reddit = praw.Reddit('tldr_generator_bot by /u/albireox')
reddit.login(os.environ['REDDIT_USERNAME'], os.environ['REDDIT_PASSWORD'])
already = bmemcached.Client((os.environ['MEMCACHEDCLOUD_SERVERS'],),
                            os.environ['MEMCACHEDCLOUD_USERNAME'],
                            os.environ['MEMCACHEDCLOUD_PASSWORD'])

subreddits = ['bottest', 'bottesting']
regex = r'(!tldr)'

for comment in praw.helpers.comment_stream(reddit, '+'.join(subreddits)):
    cid = str(comment.id)
    match = re.search(regex, comment.body, re.IGNORECASE)
    if match and not(already.get(cid)):
        try:
            summary = ' '.join(Summarize(comment.submission.title, comment.body))
            comment.reply("**TLDR:** " + summary)
            already.set(cid, "True")
        # If you are banned from a subreddit, reddit throws a 403 instead of a
        # helpful message :/
        except HTTPError as err:
            print("Probably banned from /r/" +
                  str(comment.subreddit), file=sys.stderr)
        # This one is pretty rare, since PRAW controls the rate automatically, but
        # just in case
        except praw.errors.RateLimitExceeded as err:
            print("Rate Limit Exceeded:\n" + str(err), file=sys.stderr)
            time.sleep(err.sleep_time)
