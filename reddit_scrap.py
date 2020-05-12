import sqlite3
import praw
#Here I create the database and connect.   

#creating first table with info from posts
CREATE_POST_TABLE = '''CREATE TABLE IF NOT EXISTS POSTS (
                                submission_id TEXT NOT NULL PRIMARY KEY,
                                title TEXT NOT NULL,
                                body TEXT,
                                date DATE,
                                ratio REAL NOT NULL);'''
#second table with infor from comments with foreign key to the original post
CREATE_COMMENT_TABLE = '''CREATE TABLE IF NOT EXISTS COMMENT (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                comment TEXT,
                                postid INTEGER REFERENCES POSTS(submission_id));'''

INSERT_SUBMISSION_QUERY = """INSERT INTO POSTS
                                (submission_id, title, body, date, ratio)
                                VALUES (?, ?, ?, ?,?);"""

INSERT_COMMENT_QUERY = """INSERT INTO COMMENT
                          (comment, postid) 
                          VALUES (?, ?);"""


#You can also read info from text if needed. I put * for now.
reddit = praw.Reddit(client_id="***",
                     client_secret="***",
                     user_agent="***")

#Here I create the database and connect. Init if doesnt exist yet.
def init_db(db_name):
        conn = None
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute(CREATE_POST_TABLE)
            cursor.execute(CREATE_COMMENT_TABLE)
            conn.commit()
        except sqlite3.Error as e:
            print(e)

        return conn


# function to insert post info into table
def insertPOSTS(conn, user, title, body, date, ratio):
        cursor = conn.cursor()
        cursor.execute(INSERT_SUBMISSION_QUERY, (user, title, body, date, ratio))
        conn.commit() 
        return cursor.lastrowid
        
#fuction to insert comment info into table
def insertComments(conn, comment, postid):
        cursor = conn.cursor()
        cursor.execute(INSERT_COMMENT_QUERY, (comment, postid))
        conn.commit()


# specify reddit on r/canada
subreddit = reddit.subreddit("Canada").new(limit=10)

conn = init_db('Reddit.db') # Get db instance

# collect some variables you asked for and recursively add to the respective tables.
try:
    for submission in subreddit:
        id = insertPOSTS(conn, submission.id, submission.title, submission.selftext, submission.created_utc, submission.upvote_ratio)
        print("submission has: "+ str(len(submission.comments)) +"."+ str(id))
        for comment in submission.comments:
            insertComments(conn, comment.body, id)
except: 
    print("double submissions")
    
#The try and catch is to catch the errors where you reload and have some submission id.
#10 newest reddit posts and their comments now saved to database Reddit.db in same directory where .py is run.
