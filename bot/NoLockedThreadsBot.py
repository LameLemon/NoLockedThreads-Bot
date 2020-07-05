'''
Gets posts from /r/all sorted by hot, if post is not locked, not NSFW
and not in the database, it posts to the specified subreddit.
'''
import praw
from time import sleep, strftime
from datetime import datetime
import sqlite3
from database import Database

'''
Initialise Reddit
'''
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     username='',
                     password='',
                     user_agent='Posts locked threads to specified subreddit by /u/PeskyPotato')

# Subreddit to post to
SUB = 'test'
# Subs to blackslit, e.g. ['test', 'AskReddit']
BLACKLIST = []
# Sleep between searches
SLEEP = 200
API_WAIT = 1000
# Max size of buffer
BUFFER_SIZE = 1000
# Maximum retries in case of error
MAX_RETRIES = 3
db_location = "nolockedthread.db"

''' Do not edit below this point'''
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
        try:
            if to_crosspost:
                post = submission.crosspost(SUB, title)
                post.reply("Original post: [{}]({}) \n\n----\n^[Bugs](https://www.reddit.com/message/compose?to=%2Fr%2FNoLockedThreads)".format(submission.title, link))
                return post
            else:
                post = reddit.subreddit(SUB).submit(title, url=link)
                post.reply("Original post: [{}]({}) \n\n----\n^[Bugs](https://www.reddit.com/message/compose?to=%2Fr%2FNoLockedThreads)".format(submission.title, link))
                return post
        except praw.exceptions.APIException as e:
            print(e)
            retries += 1
            if 'RATELIMIT' in str(e):
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "You are doing too much, trying to post again in 15 minutes")
                sleep(API_WAIT)
                submit(submission, True, retries)
            elif 'INVALID_CROSSPOST_THING' in str(e):
                submit(submission, False, retries)
        except Exception as e:
            print(e, submission.permalink)

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
            with open("stats.csv", "a") as stats:
                stats.write("{},{},{},{}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), submission.subreddit.display_name, submission.permalink, "0"))
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
