from flask import Blueprint, current_app, render_template, url_for
import re
from nolocked_api import api_stats, api_subreddit_count, api_subreddit_locked

nolocked = Blueprint('nolocked', __name__)

@nolocked.route('/')
def frontpage():
    stats = api_stats()

    subs = api_subreddit_count("all")
    top_subs = {
        "labels": [],
        "unlocked_posts": [],
        "locked_posts": []
    }
    for sub in subs["stats"]:
        top_subs["labels"].append(sub["subreddit"])
        top_subs["unlocked_posts"].append(sub["unlocked_posts"])
        top_subs["locked_posts"].append(sub["locked_posts"])
    
    subs_locked = api_subreddit_count("all", locked="true")
    top_locked_subs = {
        "labels": [],
        "unlocked_posts": [],
        "locked_posts": []
    }
    for sub in subs_locked["stats"]:
        top_locked_subs["labels"].append(sub["subreddit"])
        top_locked_subs["unlocked_posts"].append(sub["unlocked_posts"])
        top_locked_subs["locked_posts"].append(sub["locked_posts"])

    return render_template('nolocked/frontpage.html', 
                            stats=stats, top_subs=top_subs,
                            top_locked_subs=top_locked_subs,
                            title="Front page")

@nolocked.route('/r/<subreddit>')
def subreddit_page(subreddit):
    subreddit = re.sub(r'[\W_]+', '', subreddit)
    stats_total = api_subreddit_count(subreddit.lower())
    stats_locked = api_subreddit_count(subreddit.lower(), locked="true")
    stats_unlocked = api_subreddit_count(subreddit.lower(), locked="false")

    stats = {
        "total_posts": stats_total["stats"][0]["total_posts"],
        "locked_posts": stats_locked["stats"][0]["locked_posts"],
        "unlocked_posts": stats_unlocked["stats"][0]["unlocked_posts"]
    }
    return render_template('nolocked/subreddit.html',
                            stats=stats, subreddit=subreddit.lower(),
                            title = stats_total["stats"][0]["subreddit"])

@nolocked.route('/subreddits')
def top_subreddits():
    return render_template('nolocked/subreddits.html',
                            title="Top subreddits")
