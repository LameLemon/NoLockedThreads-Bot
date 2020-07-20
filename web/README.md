# Web server

## API Endpoints

### GET `/r/<subreddit>/count`
> Get the number of total, locked and unlocked posts per subreddit.

**Mandatory parameters**: 
* `subreddit` a case insensitive string of a subreddit

**Optional parameters**: 
| Paramter  | Type | Default | Description |
|---|---|---|---|
| locked | Boolean | none  | "true" shows only locked posts, "false" for unlocked and "none" for both |
| limit | Integer  | 20 | Number of posts to return, ordered by number of decending posts, applicable for r/all only |

**Description**
Returns the number of posts for the subreddit specified. By default the endpoint returns the total of both locked and unlocked posts, it can either returned the number of locked or unlocked by specifying `locked` to be `true` or `false`.

If the subreddit is `all` the endpoint returns the total, locked and unlocked number of posts for all subreddits from greatest number of posts to smallest. The default limit is the top 20, this can be changed with `limit` up to 100. The `locked` paramter does not apply in this case.

**Examples**
* GET http://localhost:5000/api/r/memes/count?locked=true
```json
{
    "stats": [
        {
            "locked_posts": 3,
            "subreddit": "memes"
        }
    ]
}
```

* GET http://localhost:5000/api/r/all/count?limit=2
```json
{
    "stats": [
        {
            "locked_posts": 3,
            "subreddit": "memes",
            "total_posts": 67,
            "unlocked_posts": 64
        },
        {
            "locked_posts": 1,
            "subreddit": "dankmemes",
            "total_posts": 40,
            "unlocked_posts": 39
        }
    ]
}
```
### GET `/r/api/stats`
> Get the total count of locked and unlocked posts.

**Examples**
* GET http://localhost:5000/api/r/memes/count?locked=true
```json
{
    "locked_posts": 92,
    "total_posts": 4012,
    "unlocked_posts": 3920
}
```
