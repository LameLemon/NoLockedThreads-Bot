import sqlite3

class Database:

    def __init__(self, db_location):
        self.__connection = sqlite3.connect(db_location)
        self.cursor = self.__connection.cursor()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS locked (
                id integer PRIMARY KEY,
                post_id text UNIQUE REFERENCES post(id),
                timestamp text,
                crosspost text
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS post (
                id text NOT NULL UNIQUE PRIMARY KEY, 
                title text, 
                udate text, 
                author_id int REFERENCES author(id),
                subreddit_id int REFERENCES subreddit(id)
            );
        """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS author (
                id integer PRIMARY KEY,
                name text UNIQUE
            );
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS subreddit (
                id integer PRIMARY KEY,
                name text UNIQUE
            );
        """)
    
    def add_author(self, name):
        sql = """
            INSERT INTO author (name) 
            VALUES (?)
        """
        try:
            self.cursor.execute(sql, (name,))
        except sqlite3.IntegrityError:
            print("Author {} already exists in the database".format(name))
            self.__connection.rollback()
            return None
        self.__connection.commit()
        return self.cursor.lastrowid

    def fetch_author(self, name):
        sql = """
            SELECT * FROM author WHERE name = ?
        """
        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone()

    def add_subreddit(self, name):
        sql = """
            INSERT INTO subreddit (name) 
            VALUES (?)
        """
        try:
            self.cursor.execute(sql, (name,))
        except sqlite3.IntegrityError:
            print("Subreddit {} already exists in the database".format(name))
            self.__connection.rollback()
            return None
        self.__connection.commit()
        return self.cursor.lastrowid

    def fetch_subreddit(self, name):
        sql = """
            SELECT * FROM subreddit WHERE name = ?
        """
        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone()

    def add_post(self, post_id, title, udate, author, subreddit):
        author_id = self.fetch_author(author)
        if not author_id:
            author_id = self.add_author(author)
        else:
            author_id = author_id[0]
        
        subreddit_id = self.fetch_subreddit(subreddit)
        if not subreddit_id:
            subreddit_id = self.add_subreddit(subreddit)
        else:
            subreddit_id = subreddit_id[0]
        
        sql = """
            INSERT INTO post (
                id, title, udate, author_id, subreddit_id
            ) VALUES (
                ?, ?, ?, ?, ?
            )
        """
        try:
            self.cursor.execute(sql, (post_id, title, udate, author_id, subreddit_id,))
        except sqlite3.IntegrityError:
            print("Post {} already exists in the database".format(post_id), end="\r")
            self.__connection.rollback()
            return None
        self.__connection.commit()
        return self.cursor.lastrowid

    def add_locked(self, post_id, timestamp, crosspost):
        sql = """
            INSERT INTO locked (post_id, timestamp, crosspost)
            VALUES (?, ?, ?)
        """

        try:
            self.cursor.execute(sql, (post_id, timestamp, crosspost))
        except sqlite3.IntegrityError:
            print("Submission {} already exists in databse".format(post_id))
            self.__connection.rollback()
            return None
        self.__connection.commit()
        return self.cursor.lastrowid

    def is_locked(self, post_id):
        sql = """
            SELECT * FROM locked WHERE post_id = ?
        """
        self.cursor.execute(sql, (post_id,))
        return self.cursor.fetchone()
    
    def fetch_subreddit_locked(self, subreddit_name):
        subreddit_id = self.fetch_subreddit(subreddit_name)
        if not subreddit_id:
            print("Subreddit {} does not exist in database".format(subreddit_name))
            return []
        else:
            subreddit_id = subreddit_id[0]

        sql = """
            SELECT post.title, post.id
            FROM post
            INNER JOIN locked
            WHERE post.id = locked.post_id AND post.subreddit_id = ?
        """

        self.cursor.execute(sql, (subreddit_id, ))
        return self.cursor.fetchall()

    def migrate(self, old_location):
        old_connection = sqlite3.connect(old_location)
        old_cursor = old_connection.cursor()

        self.create_tables()

        old_cursor.execute("SELECT * FROM posts")
        rows = old_cursor.fetchall()
        total = len(rows)
        count = 0
        for row in rows:
            temp = row[0].split("/")
            print("{}/{} adding {}".format(count, total, temp[2]), end="\r")
            self.add_post(temp[4], row[1], row[2], row[3], temp[2])
            self.add_locked(temp[4], 0, "")
            count += 1

    def __del__(self):
        self.__connection.close()
