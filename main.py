import flask
from flask import Flask, request, render_template, redirect, url_for
from flask_mysqldb import MySQL
import mysql.connector

connection = mysql.connector.connect(host = 'localhost', user = 'root', database = 'SmartCash', password = 'B!@ck_639928215')

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "B!@ck_639928215"
app.config['MYSQL_DB'] = "SmartCash"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


cursor = connection.cursor()

# CONNECTION STUFF ABOVE

# Create a users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL
)
""")

# Create a bank_accounts table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_number VARCHAR(20) NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Create a transactions table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(20) NOT NULL,
    transaction_type ENUM('deposit', 'withdrawal') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# Insert a fake user into the users table TESTING
fake_user_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
fake_user_values = ("hi", "hi")
cursor.execute(fake_user_query, fake_user_values)

# Commit the changes
connection.commit()
# Close the cursor and connection
cursor.close()

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # User found, redirect to a success page
            return redirect(url_for('home'))
        else:
            # User not found or incorrect credentials, redirect to login page
            return redirect(url_for('login'))
        
@app.route('/deposit', methods=['POST'])
def deposit():
    redirect(url_for('withdraw'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        account_number = request.form['account_number']

        # Update balance in the bank_accounts table
        update_query = "UPDATE bank_accounts SET balance = balance + %s WHERE account_number = %s"
        cursor.execute(update_query, (amount, account_number))

        # Insert a record into the transactions table
        transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
        cursor.execute(transaction_query, (account_number, 'deposit', amount))

        connection.commit()
        cursor.close()

        return redirect(url_for('success'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    redirect(url_for('withdraw'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        account_number = request.form['account_number']


        # Check if sufficient balance is available
        cursor.execute("SELECT balance FROM bank_accounts WHERE account_number = %s", (account_number,))
        balance = cursor.fetchone()[0]

        if balance >= amount:
            # Update balance in the bank_accounts table
            update_query = "UPDATE bank_accounts SET balance = balance - %s WHERE account_number = %s"
            cursor.execute(update_query, (amount, account_number))

            # Insert a record into the transactions table
            transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
            cursor.execute(transaction_query, (account_number, 'withdrawal', amount))

            connection.commit()
            cursor.close()

            return redirect(url_for('success'))
        else:
            return KeyError

@app.route('/transfer', methods=['POST'])
def transfer():
    if request.method == 'POST':
        sender_account = request.form['sender_account']
        receiver_account = request.form['receiver_account']
        amount = float(request.form['amount'])

        cursor = connection.cursor()

        # Check if sender has sufficient balance
        cursor.execute("SELECT balance FROM bank_accounts WHERE account_number = %s", (sender_account,))
        sender_balance = cursor.fetchone()[0]

        if sender_balance >= amount:
            # Deduct amount from sender's account
            update_sender_query = "UPDATE bank_accounts SET balance = balance - %s WHERE account_number = %s"
            cursor.execute(update_sender_query, (amount, sender_account))

            # Add amount to receiver's account
            update_receiver_query = "UPDATE bank_accounts SET balance = balance + %s WHERE account_number = %s"
            cursor.execute(update_receiver_query, (amount, receiver_account))

            # Record transaction for sender
            sender_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
            cursor.execute(sender_transaction_query, (sender_account, 'transfer (sent)', amount))

            # Record transaction for receiver
            receiver_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
            cursor.execute(receiver_transaction_query, (receiver_account, 'transfer (received)', amount))

            connection.commit()
            cursor.close()

            return redirect(url_for('success'))
        else:
            return "Insufficient balance!"

    return redirect(url_for('home'))

#REDIRECT PAGES
@app.route('/home')
def success1():
    return render_template('homepage.html')

@app.route('/success')
def success2():
    return render_template('index.html')

@app.route('/withdraw')
def success3():
    return render_template('withdraw.html')

@app.route('/transfer')
def success4():
    return render_template('transfer.html')

@app.route('/deposit')
def success5():
    return render_template('desposit.html')

@app.route('/check_balance')
def success6():
    return render_template('check_balance.html')

if __name__ == "__main__":
    app.run(debug=True)
