'''
Gets posts from /r/all sorted by hot, if post is not locked, not NSFW
and not in the database, it posts to the specified subreddit.
'''
import praw
from time import sleep, strftime
from datetime import datetime
import sqlite3
from database import Database
import yaml

with open("config.yml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print(e)

SUB = config["default"].get("subreddit", 'test')
BLACKLIST = config["default"].get("blacklist", [])
SLEEP = config["default"].get("sleep", 200)
API_WAIT = config["default"].get("api_wait", 800)
BUFFER_SIZE = config["default"].get("buffer_size", 1000)
MAX_RETRIES = config["default"].get("max_retires", 3)
db_location = config["database"].get("location", "nolockedthreads.db")

using_token = config["reddit"].get("using_token", True)
client_id = config["reddit"].get("client_id", "")
client_secret = config["reddit"].get("client_secret", "")
user_agent = config["reddit"].get("user_agent", "Posts lock threads to specified subreddit by /u/PeskyPotato")
refresh_token = config["reddit"].get("refresh_token", "")
redirect_uri = config["reddit"].get("redirect_uri", "")
username = config["reddit"].get("username", "")
password = config["reddit"].get("password", "")

if not user_agent:
    user_agent = "Posts lock threads to specified subreddit by /u/PeskyPotato"

if using_token:
    reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    refresh_token=refresh_token,
                    redirect_uri=redirect_uri)
else:
    reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)

buffer = []

'''
Checks each submission in the buffer if its not locked, not NSFW and not in blacklist,
then calls postSub on the submssion.
'''
def checkBuffer():
    size = len(buffer)
    for sub_id in buffer:
        print("checking", sub_id, "size", size, end="\r")
        submission = reddit.submission(id=sub_id)
        if submission.locked and (not submission.over_18) and str(submission.subreddit) not in BLACKLIST:
            postSub(submission)
            buffer.remove(str(submission.id))

'''
Crossposts or makes submission to targetted subreddit, waits on API errors
'''
def submit(submission, to_crosspost, retries=0):
    if retries <= MAX_RETRIES:
        link = "https://reddit.com"+submission.permalink
        title = "/r/{}: {}".format(str(submission.subreddit), submission.title)
        if len(title) > 300:
            title = title[:250] + "..."
        post = ""

        if submission.is_self:
            body = submission.selftext
        else:
            body = "[Link from post]({})".format(submission.url)

        comment_text = "Original post: [{}]({}) \n\n"\
            "Body: {}\n\n"\
            "----\n\n"\
            "^[Bugs](https://www.reddit.com/message/compose?to=%2Fr%2FNoLockedThreads)".format(submission.title, link, body)

        try:
            if to_crosspost:
                post = submission.crosspost(SUB, title)
                post.reply(comment_text)
                return post
            else:
                post = reddit.subreddit(SUB).submit(title, url=link)
                post.reply(comment_text)
                return post
        except praw.exceptions.APIException as e:
            print(e)
            retries += 1
            if 'RATELIMIT' in str(e):
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "You are doing too much, trying to post again in 15 minutes")
                sleep(API_WAIT)
                post = submit(submission, True, retries)
            elif 'INVALID_CROSSPOST_THING' in str(e):
                post = submit(submission, False, retries)
        except Exception as e:
            print(e, submission.permalink)
        return post

'''
Posts submission to targetted subreddit if does not exist in the table
'''
def postSub(submission):
    db = Database(db_location)
    db.add_post(submission.id, submission.title, submission.created, 
            str(submission.author), str(submission.subreddit))

    if not (db.is_locked(submission.id)):
        post = submit(submission, True)
        db.add_locked(submission.id, datetime.now().timestamp(), post.permalink)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Posted", submission.permalink)
        sleep(60)


'''
Gets posts from /r/all, if post is not locked, not NSFW and not on the blacklist
then calls postSub on the submission.
'''
def populateBuffer():
    if len(buffer) > BUFFER_SIZE: # trim buffer
        del buffer[:(len(buffer)-BUFFER_SIZE)]

    for submission in reddit.subreddit('all').hot(limit=1000):
        if submission.locked and (not submission.over_18) and str(submission.subreddit) not in BLACKLIST:
            postSub(submission)
        elif str(submission.id) not in buffer:
            db = Database(db_location)
            db.add_post(submission.id, submission.title, submission.created, 
                        str(submission.author), str(submission.subreddit))
            buffer.append(str(submission.id))

def main():
    while(1):
        populateBuffer()
        checkBuffer()
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Sleeping for", SLEEP, "seconds.")
        sleep(SLEEP)

'''
Initialise bot
'''
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        sleep(120)
        main()
