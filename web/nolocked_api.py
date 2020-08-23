from flask import Blueprint, current_app, request
from database import Database
import sqlite3

nolocked_api = Blueprint('nolocked_api', __name__)

@nolocked_api.route('/')
def api_root():
    return "you wot m8"

@nolocked_api.route('/r/<subreddit>/count')
def api_subreddit_count(subreddit, locked="", limit=20):
    subreddit = subreddit.lower()
    if locked == "":
        locked = request.args.get("locked", default="")

    if locked.lower() == "false":
        locked = False
    elif locked.lower() == "true":
        locked = True
    else:
        locked = None

    if limit == 20:
        limit = request.args.get("limit", default=20, type=int)
    if limit > 100:
        limit = 100
    print(limit)
    db = Database(current_app.config["NLT_DB"])
    posts = db.count_subreddit(subreddit, locked, limit)
    res = []
    if subreddit != "all":
        if locked == True:
            if not posts:
                res.append({
                    "subreddit": subreddit,
                    "locked_posts": 0
                })
            else:
                res.append({
                    "subreddit": posts[0][0],
                    "locked_posts": posts[0][1],
                })
        elif locked == False:
            if not posts:
                res.append({
                    "subreddit": subreddit,
                    "unlocked_posts": 0,
                })
            else:
                res.append({
                    "subreddit": posts[0][0],
                    "unlocked_posts": posts[0][1],
                })
        else:
            if not posts:
                res.append({
                    "subreddit": subreddit,
                    "total_posts": 0,
                })
            else:
                res.append({
                    "subreddit": posts[0][0],
                    "total_posts": posts[0][1],
                })
    for post in posts:
        if subreddit == "all":
            locked_posts = db.count_subreddit(post[0], True)
            if locked_posts:
                locked_posts = locked_posts[0][1]
            else: 
                locked_posts = 0
            unlocked_posts = db.count_subreddit(post[0], False)
            if unlocked_posts:
                unlocked_posts = unlocked_posts[0][1]
            else: 
                unlocked_posts = 0
            res.append({
                "subreddit": post[0],
                "total_posts": post[1],
                "locked_posts": locked_posts,
                "unlocked_posts": unlocked_posts
            })
    return {"stats": res}

@nolocked_api.route('/stats')
def api_stats():
    db = Database(current_app.config["NLT_DB"])
    all_posts = db.post_stats_all()
    locked_posts = db.post_stats_locked()

    return {
        "total_posts": all_posts[0][0],
        "locked_posts": locked_posts[0][0],
        "unlocked_posts": db.post_stats_unlocked()[0][0]
    }

@nolocked_api.route('/r/<subreddit>')
def api_subreddit_locked(subreddit, locked=""):
    if locked == "":
        locked = request.args.get("locked", default="")
    if locked.lower() == "false":
        locked = False
    elif locked.lower() == "true":
        locked = True
    else:
        locked = None

    limit = request.args.get("limit", default=10, type=int)
    if limit > 50:
        limit = 50

    offset = request.args.get("offset", default=0, type=int)

    sort = request.args.get("sort", default="DESC")
    if sort.lower() == "asc":
        sort = "asc"

    db = Database(current_app.config["NLT_DB"])
    posts = db.fetch_subreddit_locked(subreddit, locked, limit, offset, sort)
    res = {
        "posts": []
    }
    for post in posts:
        res["posts"].append({
            "id": post[0],
            "title": post[1],
            "created_utc": post[2], # udate in db
            "author": post[3],
            "subreddit": post[4],
            "crosspost": post[5],
            "locked_utc": post[6],
            "locked": post[7]
        })
    return res

