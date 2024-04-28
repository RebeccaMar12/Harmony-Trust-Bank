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

# Insert a fake user into the users table
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

#herererererereeeeeeeeeeeeeeeeeee
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # User found, redirect to a success page
            return redirect(url_for('success'))
        else:
            # User not found or incorrect credentials, redirect to login page
            return redirect(url_for('home'))

@app.route('/success')
def success():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
