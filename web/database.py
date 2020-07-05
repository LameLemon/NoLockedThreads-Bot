import sqlite3

class Database:

    def __init__(self, db_location):
        self.__connection = sqlite3.connect(db_location)
        self.cursor = self.__connection.cursor()

    def fetch_author(self, name):
        sql = """
            SELECT * FROM author WHERE name = ?
        """
        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone()

    def fetch_subreddit(self, name):
        sql = """
            SELECT * FROM subreddit WHERE name = ?
        """
        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone()

    def is_locked(self, post_id):
        sql = """
            SELECT * FROM locked WHERE post_id = ?
        """
        self.cursor.execute(sql, (post_id,))
        return self.cursor.fetchone()
    
    def fetch_subreddit_locked(self, subreddit_name, locked=None, limit=10, offset=0, sort="desc"):
        if subreddit_name == "all" and locked:
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                INNER JOIN locked ON locked.post_id = post.id
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)
        elif subreddit_name == "all" and locked == None:
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                LEFT JOIN locked ON (post.id  = locked.post_id)
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)
        elif subreddit_name == "all" and not locked:
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                LEFT JOIN locked ON (post.id  = locked.post_id)
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                WHERE locked.post_id IS NULL
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)
        elif locked == None: # both locked and unlocked
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                LEFT JOIN locked ON (post.id  = locked.post_id)
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                WHERE subreddit.name = ? COLLATE NOCASE
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)
        elif locked: # locked only
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                INNER JOIN locked ON locked.post_id = post.id
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                WHERE subreddit.name = ? COLLATE NOCASE
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)
        else: # unlocked only
            sql = """
                SELECT post.id, post.title, post.udate, author.name, subreddit.name,
                    locked.crosspost, locked.timestamp,
                    CASE
                        WHEN locked.post_id IS NULL THEN 0 ELSE 1 
                    END AS locked
                FROM post
                INNER JOIN author ON author.id = post.author_id
                INNER JOIN subreddit ON subreddit.id = post.subreddit_id
                LEFT JOIN locked on (post.id = locked.post_id)
                WHERE locked.post_id IS NULL AND subreddit.name = ? COLLATE NOCASE
                ORDER BY udate {}
                LIMIT ?
                OFFSET ?
            """.format(sort)

        if subreddit_name == "all":
            values = (limit, offset)
        else:
            values = (subreddit_name, limit, offset)
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def count_subreddit(self, subreddit_name, locked=None, limit=20):
        if subreddit_name == "all" and (locked!= True):
            sql = """
                SELECT subreddit.name, count(subreddit.id) as subreddit_count        
                FROM post
                LEFT JOIN subreddit ON (subreddit.id = post.subreddit_id)
                WHERE post.udate > 1593820800
                GROUP BY post.subreddit_id
                ORDER BY subreddit_count DESC
                LIMIT ?
            """
            values = (limit, )
        elif subreddit_name == "all" and locked:
            sql = """
                SELECT subreddit.name, count(subreddit.id) as subreddit_count        
                FROM post
                LEFT JOIN subreddit ON (subreddit.id = post.subreddit_id)
                INNER JOIN locked ON locked.post_id = post.id
                WHERE post.udate > 1593820800
                GROUP BY post.subreddit_id
                ORDER BY subreddit_count DESC
                LIMIT ?
            """
            values = (limit, )
        elif locked == None:
            sql = """
                SELECT subreddit.name, count(subreddit.id) as subreddit_count        
                FROM post
                LEFT JOIN subreddit ON (subreddit.id = post.subreddit_id)
                LEFT JOIN locked ON locked.post_id = post.id
                WHERE subreddit.name = ? COLLATE NOCASE AND post.udate > 1593820800
                GROUP BY post.subreddit_id
                ORDER BY subreddit_count DESC
            """
            values = (subreddit_name, )
        elif locked:
            sql = """
                SELECT subreddit.name, count(subreddit.id) as subreddit_count        
                FROM post
                LEFT JOIN subreddit ON (subreddit.id = post.subreddit_id)
                INNER JOIN locked ON locked.post_id = post.id
                WHERE subreddit.name = ? COLLATE NOCASE AND post.udate > 1593820800
                GROUP BY post.subreddit_id
                ORDER BY subreddit_count DESC
            """
            values = (subreddit_name, )
        elif not locked:
            sql = """
                SELECT subreddit.name, count(subreddit.id) as subreddit_count        
                FROM post
                LEFT JOIN subreddit ON (subreddit.id = post.subreddit_id)
                LEFT JOIN locked ON locked.post_id = post.id
                WHERE locked.post_id IS NULL AND subreddit.name = ? COLLATE NOCASE AND post.udate > 1593820800
                GROUP BY post.subreddit_id
                ORDER BY subreddit_count DESC
            """
            values = (subreddit_name, )

        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def post_stats_all(self):
        sql = """
            SELECT COUNT(*) FROM post
            WHERE post.udate > 1593820800
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def post_stats_locked(self):
        sql = """
            SELECT COUNT(*) FROM post
            INNER JOIN locked ON locked.post_id = post.id
            WHERE post.udate > 1593820800
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def post_stats_unlocked(self):
        sql = """
            SELECT COUNT(*) FROM post
            LEFT JOIN locked ON locked.post_id = post.id
            WHERE locked.post_id IS NULL AND post.udate > 1593820800
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def __del__(self):
        self.__connection.close()
