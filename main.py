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
    
# If a user table isn't already there, it makes one
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL
)
""")

# If the bank account table isn't already there, it makes one
cursor.execute("""
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_number VARCHAR(20) NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# If a transactions table isn't already there, it will add one
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(20) NOT NULL,
    transaction_type ENUM('deposit', 'withdrawal') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# Put a falso user into a user table, to test it
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
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
        
@app.route('/deposit', methods=['POST'])
def deposit():
    redirect(url_for('withdraw'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        account_number = request.form['account_number']

        # The bank account table's balance shoudl be updated
        update_query = "UPDATE bank_accounts SET balance = balance + %s WHERE account_number = %s"
        cursor.execute(update_query, (amount, account_number))

        # Add a record to the table of transactions
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


        # Verify if there is an adequate balance avaiible 
        cursor.execute("SELECT balance FROM bank_accounts WHERE account_number = %s", (account_number,))
        balance = cursor.fetchone()[0]

        # Incorporates a record into the transactions table and update the balance in the bank account table
        if balance >= amount:
          
            update_query = "UPDATE bank_accounts SET balance = balance - %s WHERE account_number = %s"
            cursor.execute(update_query, (amount, account_number))

    
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

        # Verify if the sender has an adequate balance avaiible 
        cursor.execute("SELECT balance FROM bank_accounts WHERE account_number = %s", (sender_account,))
        sender_balance = cursor.fetchone()[0]

        #Take money out of the sender's account, add monet to the recipent's account, both sender and the recipient's transaction should be recorded.
        if sender_balance >= amount:
            update_sender_query = "UPDATE bank_accounts SET balance = balance - %s WHERE account_number = %s"
            cursor.execute(update_sender_query, (amount, sender_account))

            update_receiver_query = "UPDATE bank_accounts SET balance = balance + %s WHERE account_number = %s"
            cursor.execute(update_receiver_query, (amount, receiver_account))

            sender_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
            cursor.execute(sender_transaction_query, (sender_account, 'transfer (sent)', amount))

            receiver_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)"
            cursor.execute(receiver_transaction_query, (receiver_account, 'transfer (received)', amount))

            connection.commit()
            cursor.close()

            return redirect(url_for('success'))
        else:
            return "Insufficient balance!"

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
