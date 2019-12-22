import os

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
import json
import sqlite3
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    stocks = db.execute("SELECT symbol, SUM(shares) as shares FROM history WHERE id=:id GROUP BY symbol",
                        id=session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id =:id", id=session["user_id"])
    cash = cash[0]["cash"]

    total = 0
    for stock in stocks:
        stock["price"] = lookup(stock["symbol"])["price"]
        stock["total"] = stock["price"] * stock["shares"]
        stock["name"] = lookup(stock["symbol"])["name"]
        total += stock["total"]
        stock["price"] = '{:.2f}'.format(stock["price"])
        stock["total"] = '{:.2f}'.format(stock["total"])
    total += cash
    return render_template("index.html",
                           stocks=stocks,
                           cash='{:.2f}'.format(cash),
                           total='{:.2f}'.format(total))


def is_string_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)

        # Ensure share was submitted
        elif not request.form.get("shares"):
            return apology("must provide shares", 403)

        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol", 400)

        shares = request.form.get("shares")
        if not is_string_int(shares):
            return apology("number of shares has to be a positive number", 400)
        else:
            shares = int(shares)
        if shares <= 0:
            return apology("number of shares has to be a positive number", 400)

        # Check if the user can afford
        cash = db.execute("SELECT cash FROM users WHERE id =:id", id=session["user_id"])
        cash = cash[0]["cash"]

        price = quote["price"]
        current_cash = cash - (shares * price)
        if current_cash < 0:
            return apology("you can't afford ")
        # if alright
        # update the cash in users table
        db.execute("UPDATE users SET cash =:current_cash WHERE id=:id", id=session["user_id"], current_cash=current_cash)
        # update the portfolio
        rows = db.execute("SELECT * FROM portfolio WHERE id=:id AND symbol=:symbol", id=session["user_id"], symbol=symbol)
        if len(rows) == 0:
            db.execute("INSERT INTO portfolio (id, symbol, shares) VALUES(:id, :symbol, :shares)",
                       id=session["user_id"], symbol=symbol, shares=shares)
        else:
            db.execute("UPDATE portfolio SET shares = shares + :shares WHERE id =:id", shares=shares, id=session["user_id"])

        # update the history table
        transacted = datetime.now()
        db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES (:id, :symbol, :shares, :price, :transacted)",
                   id=session["user_id"], symbol=symbol, shares=shares, price=price, transacted=transacted)

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route('/<username>', methods=["GET"])
def check(username):
    """Return true if username available, else false, in JSON format"""
    username = request.args.get('username', type=str)
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=username)
    if rows:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    histories = db.execute("SELECT *  FROM history WHERE id=:id",
                           id=session["user_id"])

    return render_template("history.html", histories=histories)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST
    if request.method == "POST":
        # check if quote form was submitted
        if not request.form.get("symbol"):
            return apology("Missing symbol")

        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        # Validate symbol
        if quote is None:
            return apology("Wrong symbol")

        return render_template("quoted.html",
                               symbol=symbol,
                               name=quote["name"],
                               price='{:.2f}'.format(quote["price"]))
    else:
        return render_template("quote.html")


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

        is_available = json.loads(check(username).response[0])
        #is_available = check(username)
        if not is_available:
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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # require that a user input a stock’s symbol
        # render an apology if the user fails to select a stock

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure share was submitted
        if not request.form.get("shares"):
            return apology("must provide shares", 400)

        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)

        if not quote:
            return apology("invalid symbol", 400)
        price = quote["price"]

        shares = request.form.get("shares")
        if not is_string_int(shares):
            return apology("number of shares has to be a positive number", 400)
        else:
            shares = int(shares)
        if shares <= 0:
            return apology("number of shares has to be a positive number", 400)

        # implemented as a select menu whose name is symbol.
        shares_owned = db.execute("SELECT shares FROM portfolio WHERE id =:id and symbol= :symbol",
                                  id=session["user_id"],
                                  symbol=symbol)
        # render an apology  if the user does not own any shares of that stock.
        if len(shares_owned) == 0:
            return apology("You don't owned this stock", 400)

        shares_owned = shares_owned[0]["shares"]
        shares_update = shares_owned - shares

        if shares > shares_owned:
            return apology("To much", 400)

        cash_update = shares * price

        # Update the cash user table- dobrze
        db.execute("UPDATE users SET cash = cash + :cash_update WHERE id =:id",
                   cash_update=cash_update, id=session["user_id"])

        # Update portfolio table
        if shares_update == 0:

            db.execute("DELETE from portfolio WHERE id =:id AND symbol=:symbol", id=session["user_id"], symbol=symbol)

        elif shares_update > 0:
            db.execute("UPDATE portfolio SET shares = shares + :shares_update WHERE id =:id",
                       shares_update=shares_update, id=session["user_id"])

        # Update history table
        transacted = datetime.now()
        db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES (:id, :symbol, :shares, :price, :transacted)",
                   id=session["user_id"], symbol=symbol, shares=-(shares), price=price, transacted=transacted)

        return redirect("/")
    else:
        stocks = db.execute("SELECT symbol FROM portfolio WHERE id=:id",
                            id=session["user_id"])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


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
