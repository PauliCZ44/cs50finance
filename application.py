import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
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
#db = SQL("sqlite:///finance.db")
db = SQL(os.getenv("DATABASE_URL"))

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id;",  user_id = session["user_id"])[0]["cash"]

    # Select only stocks of logged user, summed by name of company.
    # rows = db.execute("SELECT name, symbol, price, sum(amount) AS amount FROM stocks WHERE user_id = :user_id DISTINCT ON name;",  user_id = session["user_id"])
    rows = db.execute("SELECT name, symbol, sum(amount) AS  amount FROM stocks WHERE user_id = :user_id GROUP BY name, symbol;",  user_id = session["user_id"])

    #rows2 = db.execute("SELECT name, symbol, price FROM stocks WHERE user_id = :user_id  ")
    total_value = 0

    for row in rows:
        # in each row (already summed) take for a actual price. Sum total value of stocks as you go.
        row["actual_price"] = lookup(row["symbol"])["price"]
        total_value += row["actual_price"]*row["amount"]

    # FIlter rows to show only non-zero stocks  - ispired by   https://www.geeksforgeeks.org/python-removing-dictionary-from-list-of-dictionaries/
    filtered_rows = list(filter(lambda i: i['amount'] != 0, rows))

    # since you can not use functions directly in templates, you haveto pass functions to them usd = usd
    return render_template("index.html", user_cash = user_cash, rows = filtered_rows, usd = usd, total = total_value)

# TEST
@app.route("/index2")
@login_required
def test():
    """Show portfolio of stocks"""

    user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id;",  user_id = session["user_id"])[0]["cash"]

    # Select only stocks of logged user, summed by name of company.
    rows = db.execute("SELECT name, symbol, price, sum(amount) AS amount FROM stocks WHERE user_id = :user_id GROUP BY name;",  user_id = session["user_id"])
    total_value = 0

    for row in rows:
        # in each row (already summed) take for a actual price. Sum total value of stocks as you go.
        row["actual_price"] = lookup(row["symbol"])["price"]
        total_value += row["actual_price"]*row["amount"]

    # FIlter rows to show only non-zero stocks  - ispired by   https://www.geeksforgeeks.org/python-removing-dictionary-from-list-of-dictionaries/
    filtered_rows = list(filter(lambda i: i['amount'] != 0, rows))

    # since you can not use functions directly in templates, you haveto pass functions to them usd = usd
    return render_template("index2.html", user_cash = user_cash, rows = filtered_rows, usd = usd, total = total_value)

##END TEST
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id;",  user_id = session["user_id"])
        return render_template("buy.html", user_cash = usd(user_cash[0]["cash"]))

    if request.method == "POST":
        amount = float(request.form.get("stockAmount"))
        symbol = request.form.get("stocksymbol")

        if symbol == "" :
            return apology("Please fill in a stock symbol")

        # Find symbol and price, check response
        res = lookup(symbol)
        if res == None :
            return apology("symbol not found")
        if amount < 1:
            return apology("Amount must be greater than 0!")

        total_price = amount * float(res["price"])
        user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id",  user_id = session["user_id"])[0]["cash"]

        if total_price > user_cash:
            return apology("Not enough money to buy.")
        else:
            db.execute("INSERT INTO stocks(user_id, symbol, name, amount, price)  VALUES (:user_id, :symbol, :name, :amount, :price);",
                          user_id=session["user_id"], symbol=res["symbol"], name=res["name"], amount=amount, price=res["price"])
            db.execute("UPDATE users SET cash = :new_cash WHERE id  = :user_id;", new_cash = (user_cash-total_price), user_id = session["user_id"])
            message = "Bought " + str(int(amount)) + " stocks of " + symbol.upper() + " for " + usd(total_price)
            flash(message)
            return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM stocks WHERE user_id = :user_id", user_id = session["user_id"])
    for row in rows:
        if row["amount"] < 0:
            row["text_color"] = "red-text"
        else:
            row["text_color"] = "normal-text"

    return render_template("history.html", rows = rows, usd = usd)


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
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        symbol = request.form.get("stocksymbol")
        if symbol == "" :
            return apology("Please fill in a stock symbol")
        res = lookup(symbol)
        if res == None :
            return apology("symbol not found")
        price = usd(res["price"])
        return render_template("quote2.html", name = res["name"], price = price, symbol = res["symbol"], )


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        """Create user in DB"""
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        passwordConfirm = request.form.get("passwordConfirm")

        if(passwordConfirm != request.form.get("password")):
            return apology("Your password did not match", 403)

        #Check for take nusername
        existing_username = db.execute("SELECT username FROM users WHERE username = :username",
                          username=username)
        if(len(existing_username) != 0):
            return apology("username is already taken", 403)


        # Query database to create an user in user table
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                          username=username, password=password)
        return redirect("/")
    elif request.method == "GET":
        """Show REgistration for"""
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id;",  user_id = session["user_id"])
        user_stocks = db.execute("SELECT symbol, sum(amount) AS amount FROM stocks WHERE user_id = :user_id GROUP BY symbol;", user_id = session["user_id"])
        return render_template("sell.html", user_cash = usd(user_cash[0]["cash"]), rows = user_stocks)
    if request.method == "POST":
        amount = float(request.form.get("stockAmount"))
        symbol = request.form.get("stocksymbol")
        print(symbol)
        if symbol == "" or symbol == None :
            return apology("Please fill in a stock symbol.")
        res = lookup(symbol)
        print(res)
        if res == None :
            return apology("Symbol not found.")
        if amount < 1:
            return apology("Amount must be greater than 0!")
        total_price = amount * float(res["price"])
        user_stocks = db.execute("SELECT symbol, sum(amount) AS amount FROM stocks WHERE user_id = :user_id AND symbol = :symbol GROUP BY symbol;", user_id = session["user_id"], symbol=res["symbol"])
        if amount > user_stocks[0]["amount"]:
            return apology("You dont have enough stocks to sell.")
        user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id",  user_id = session["user_id"])[0]["cash"]
        db.execute("INSERT INTO stocks(user_id, symbol, name, amount, price)  VALUES (:user_id, :symbol, :name, :amount, :price);",
            user_id=session["user_id"], symbol=res["symbol"], name=res["name"], amount=amount*(-1), price=res["price"])
        db.execute("UPDATE users SET cash = :new_cash WHERE id  = :user_id;", new_cash = (user_cash+total_price), user_id = session["user_id"])
        message = "Sold " + str(int(amount)) + " stocks of " + symbol.upper() + " for " + usd(total_price)
        flash(message)
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
