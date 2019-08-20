'''
Gets posts from /r/all sorted by hot, if post is not locked, not NSFW
and not in the database, it posts to the specified subreddit.
'''
import praw
from time import sleep, strftime
from datetime import datetime
import sqlite3

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

''' Do not edit below this point'''
buffer = []
comment_tree = ""

'''
Creates a database file and table if one does not already exist.
'''
def createTable():
    conn = sqlite3.connect('posted.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts (perma TEXT NOT NULL UNIQUE, title TEXT, udate TEXT, author TEXT, PRIMARY KEY (perma))')
    c.close()
    conn.close()

'''
Writes post to table, if the post exists returns a 0 else 1.
'''
def dbWrite(perma, title, udate, author):
    try:
        conn = sqlite3.connect('posted.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (perma, title, udate, author) VALUES (?, ?, ?, ?)", (perma, title, udate, str(author)))
        conn.commit()
    except sqlite3.IntegrityError:
        c.close()
        conn.close()
        return 0

    c.close()
    conn.close()
    return 1

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
            with open("stats.csv", "a") as stats:
                stats.write("{},{},{},{}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), submission.subreddit.display_name, submission.permalink, "1"))

            buffer.remove(str(submission.id))

'''
Gets a comment tree
'''
def parse_comment(comment, author, is_root=True):
    global comment_tree
    comment_author = ""
    try:
        comment_author = comment.author.name
    except AttributeError:
        comment_author = "None"

    if is_root:
        comment_tree += "    Author: {} Body: {}\n\n".format(comment_author, str(comment.body).replace("\n", "    "))
    else:
        comment_tree += "        Author: {} Body: {}\n\n".format(comment_author, str(comment.body.replace("\n", "       ")))

    for reply in comment.replies[:2]:
        if isinstance(reply, praw.models.MoreComments):
            continue
        parse_comment(reply, author, False)

'''
Crossposts or makes submission to targetted subreddit, waits on API errors
'''
def submit(submission, to_crosspost, retries=0):
    if retries <= MAX_RETRIES:
        global comment_tree
        link = "https://reddit.com"+submission.permalink
        title = "/r/{}: {}".format(str(submission.subreddit), submission.title)
        if len(title) > 300:
            title = title[:250] + "..."
        post = ""
        try:
            if to_crosspost:
                post = submission.crosspost(SUB, title)
                comment_tree = ""
                for comment in submission.comments:
                    if isinstance(comment, praw.models.MoreComments):
                        continue
                    if len(comment_tree) > 2500:
                        break
                    parse_comment(comment, submission.author)
                post.reply("Original post: [{}]({}) \n\nComments:\n\n{}\n\n----\n^[Bugs](https://www.reddit.com/message/compose?to=%2Fr%2FNoLockedThreads)".format(submission.title, link, comment_tree))
            else:
                post = reddit.subreddit(SUB).submit(title, url=link)
                comment_tree = ""
                for comment in submission.comments:
                    if isinstance(comment, praw.models.MoreComments):
                        continue
                    if len(comment_tree) > 2500:
                        break
                    parse_comment(comment, submission.author)
                post.reply("Original post: [{}]({}) \n\nComments:\n\n{}\n\n----\n^[Bugs](https://www.reddit.com/message/compose?to=%2Fr%2FNoLockedThreads)".format(submission.title, link, comment_tree))

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
    if(dbWrite(submission.permalink, submission.title, submission.created, submission.author)):
        submit(submission, True)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Posted", submission.permalink)
        sleep(60)


'''
Gets posts from /r/all, if post is not locked, not NSFW and not on the blacklist
then calls postSub on the submission.
'''
def populateBuffer():
    if len(buffer) > BUFFER_SIZE:
        del buffer[:(len(buffer)-BUFFER_SIZE)]
    for submission in reddit.subreddit('all').hot(limit=1000):
        if submission.locked and (not submission.over_18) and str(submission.subreddit) not in BLACKLIST:
            postSub(submission)
            with open("stats.csv", "a") as stats:
                stats.write("{},{},{},{}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), submission.subreddit.display_name, submission.permalink, "0"))
        elif str(submission.id) not in buffer:
            buffer.append(str(submission.id))
def main():
    while(1):
        createTable()
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
