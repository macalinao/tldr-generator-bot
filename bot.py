"""
**someredditusername by /u/you**
*Inspired by /u/person on /r/RequestABot*

This bot just finds comments in a list
of subreddits with the word "gist" in the
body and replies with a small comment.
"""

from __future__ import print_function
import praw
import bmemcached
import time
import os

from requests import HTTPError
import sys

import re
import textwrap
from pyteaser import Summarize

reddit = praw.Reddit('tldr_generator_bot by /u/albireox')

print(os.environ.get('REDDIT_USERNAME'))

reddit.login(os.environ['REDDIT_USERNAME'], os.environ['REDDIT_PASSWORD'])
already = bmemcached.Client((os.environ['MEMCACHEDCLOUD_SERVERS'],),
                            os.environ['MEMCACHEDCLOUD_USERNAME'],
                            os.environ['MEMCACHEDCLOUD_PASSWORD'])

subreddits = ['bottest', 'bottesting']
regex = r'(!tldr)'

for comment in praw.helpers.comment_stream(reddit, '+'.join(subreddits)):
    cid = str(comment.id)
    match = re.search(regex, comment.body, re.IGNORECASE)

    print("Scanning comments...")

    if match and not(already.get(cid)):
        try:
            summary = ' '.join(
                Summarize(comment.submission.title, comment.body))
            comment.reply("**TLDR:** " + summary)
            already.set(cid, "True")
            print("Summarized!")

        except HTTPError as err:
            print("Probably banned from /r/" +
                  str(comment.subreddit), file=sys.stderr)

        except praw.errors.RateLimitExceeded as err:
            print("Rate Limit Exceeded:\n" + str(err), file=sys.stderr)
            time.sleep(err.sleep_time)
