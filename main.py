import flask
from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "B!@ck_639928215"
app.config['MYSQL_DB'] = "SmartCash"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

connection = mysql.connector.connect(host = 'localhost', user = 'root', database = 'SmartCash', password = 'B!@ck_639928215')
                                     
cursor = connection.cursor()

