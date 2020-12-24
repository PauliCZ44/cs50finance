This is a website via which users can “buy” and “sell” stocks with virtual cash.

#Specification
##register
Complete the implementation of register in such a way that it allows a user to register for an account via a form.

Require that a user input a username, implemented as a text field whose name is username. Render an apology if the user’s input is blank or the username already exists.
Require that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation. Render an apology if either input is blank or the passwords do not match.
Submit the user’s input via POST to /register.
INSERT the new user into users, storing a hash of the user’s password, not the password itself. Hash the user’s password with generate_password_hash Odds are you’ll want to create a new template (e.g., register.html) that’s quite similar to login.html.
Once you’ve implemented register correctly, you should be able to register for an account and log in (since login and logout already work)! And you should be able to see your rows via phpLiteAdmin or sqlite3.

##quote
Complete the implementation of quote in such a way that it allows a user to look up a stock’s current price.

Require that a user input a stock’s symbol, implemented as a text field whose name is symbol.
Submit the user’s input via POST to /quote.
Odds are you’ll want to create two new templates (e.g., quote.html and quoted.html). When a user visits /quote via GET, render one of those templates, inside of which should be an HTML form that submits to /quote via POST. In response to a POST, quote can render that second template, embedding within it one or more values from lookup.

##buy
Complete the implementation of buy in such a way that it enables a user to buy stocks.

##index
Complete the implementation of index in such a way that it displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

##sell
Complete the implementation of sell in such a way that it enables a user to sell shares of a stock (that he or she owns).

Require that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of that stock.
Require that a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer or if the user does not own that many shares of the stock.
Submit the user’s input via POST to /sell.
You don’t need to worry about race conditions (or use transactions).

##history
Complete the implementation of history in such a way that it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.

For each row, make clear whether a stock was bought or sold and include the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.
You might need to alter the table you created for buy or supplement it with an additional table. Try to minimize redundancies.