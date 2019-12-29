import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import json
import re
import sqlite3
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)#, template_folder='templates')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = tempfile.mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.route("/tags")
def tags():
    # get tags and number of posts with the tag
    tag_data = db.execute(
        "select tag, count(*) as count_tag FROM post_tag GROUP BY tag ORDER BY count_tag DESC"
    )
    return render_template("tags.html", tag_data=tag_data)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/<tag>', methods=["GET"])
def subjects(tag):
    # get all posts with given tag
    posts = db.execute("SELECT * FROM posts WHERE id IN (SELECT post_id FROM post_tag WHERE tag=:tag)", tag=tag)
    return render_template("subjects.html", posts=posts)


@app.route('/subjects_search', methods=["GET", "POST"])
def subjects_search():
    # get all posts with given tag
    if request.method == "POST":
        tags = request.form.get("search_tags")
        tags = [re.sub('[^A-Za-z0-9 ]+', '', x.strip()) for x in tags.split(',')]

        placeholder= '?'
        placeholders= ', '.join(placeholder for _ in tags)
        query = "SELECT * FROM posts WHERE id IN (SELECT post_id FROM post_tag WHERE tag IN (%s))" % placeholders
        posts = db.execute(query, tags)
        return render_template("subjects.html", posts=posts)
    else:
        return render_template("post_template.html")

@app.route('/show_subject/<id>', methods=["GET"])
def show_subject(id):
    post = db.execute("SELECT * FROM posts WHERE id=:id", id=int(id))
    post[0]["user"] = db.execute("SELECT username FROM users WHERE id=:id", id=post[0]["user_id"])[0]["username"]
    replies = db.execute("SELECT post_replies.reply_content, post_replies.date, users.username FROM post_replies INNER JOIN users ON post_replies.user_id=users.id  WHERE post_replies.original_post_id=:id", id=int(id))

    return render_template("show_subject.html", post=post[0], replies=replies, original_post_id=id)


@login_required
@app.route("/post_template", methods=["GET", "POST"])
def post_template():
    if request.method == "POST":
        time = datetime.now()
        post_content = request.form.get("post_content")
        subject = request.form.get("subject")

        tags = request.form.get("tags")
        tags = [re.sub('[^A-Za-z0-9 ]+', '', x.strip()) for x in tags.split(',')]
        if len(tags) > 10:
            tags = tags[:10]

        if (not post_content or not subject or tags == ['']):
            raise NotImplementedError("TODO: uzupelnij error gdy formularz nie jest wypleniony")

        # insert tags to the tag table
        for tag in tags:
            db.execute("INSERT INTO tags (name) VALUES (:tag)", tag=tag)


        ids = db.execute("SELECT id FROM posts")
        if len(ids) > 0:
            post_id = ids[-1]["id"] + 1
        else:
            post_id = 1

        # insert tags to the post_tag table
        for tag in tags:
            db.execute("INSERT INTO post_tag (post_id, tag) VALUES (:post_id, :tag)",
                       post_id=post_id, tag=tag)

        db.execute("INSERT INTO posts (user_id, post, subject, post_date) VALUES (:user_id, :post, :subject,:post_date)",
                   user_id=session["user_id"], post=post_content, subject=subject, post_date=time)
        return redirect("/show_subject/{}".format(post_id))

    else:
        return render_template("post_template.html")


@login_required
@app.route("/post_reply", methods=["GET", "POST"])
def post_reply():
    if request.method == "POST":
        time = datetime.now()
        original_post_id = request.form.get("original_post_id")
        post_content = request.form.get("reply_content")
        post_replies = db.execute("SELECT id FROM post_replies")
        if len(post_replies) > 0:
            post_id = post_replies[-1]["id"] + 1
        else:
            post_id = 1
        if not post_content:
            raise NotImplementedError("TODO: uzupelnij error gdy formularz nie jest wypleniony")
        db.execute("INSERT INTO post_replies (original_post_id, user_id, reply_content, date) VALUES (:original_post_id, :user_id, :reply_content,:date)",
                   original_post_id=int(original_post_id), user_id=session["user_id"], reply_content=post_content, date=time)
        return redirect("/show_subject/{}".format(original_post_id))

    else:
        return render_template("post_template.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 400)
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not is_user_available(username):
            return apology("provided username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        # Ensure passwords match
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("Password doesn't match!", 400)

        # Add user to databse
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            username=username,
                            hash=generate_password_hash(request.form.get("password")))
        if not result:
            return apology("rrr")

        # Remember which user has logged in
        session["user_id"] = result
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def is_user_available(username):
    """Return True if username is available, else false"""
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=username)
    return False if rows else True


@app.route("/passwords", methods=["GET", "POST"])
@login_required
def change_passwords():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # change passwords for user loggedin

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure old password was submitted
        elif not request.form.get("old_password"):
            return apology("must provide password", 403)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide password", 403)

        # Ensure password was confirmed
        elif not request.form.get("new_password_confirmation"):
            return apology("must confirm password", 403)

        # Ensure passwords match
        elif request.form.get("new_password_confirmation") != request.form.get("new_password"):
            return apology("Password doesn't match!", 403)

        current_hash = db.execute("SELECT hash FROM users WHERE id =:id",
                                  id=session["user_id"])
        if check_password_hash(current_hash[0]['hash'],
                               generate_password_hash(request.form.get("old_password"))):
            return apology("old password is wrong", 403)

        db.execute("UPDATE users SET hash =:hash WHERE id=:id",
                   id=session["user_id"], hash=generate_password_hash(request.form.get("new_password")))
        flash("password changed")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("passwords.html")

@app.route("/description", methods=["GET", "POST"])
def description():

    if request.method == "POST":
        return render_template("description.html")
    else:
        return render_template("description.html")