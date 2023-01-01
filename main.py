import mysql
import mysql.connector as sql
import http.server
import socketserver
import routes
import web
from flask import Flask, render_template

# Connect to the MySQL database
cnx = mysql.connector.connect(user='root', password='1234',
                              host='localhost', database='bibels')
cursor = cnx.cursor()


# Create the Flask app
app = Flask(__name__)

# Define the request handlers
@app.route('/table/<table>/<book_no>')
def table(table, book_no):
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, book_no))
    rows = cursor.fetchall()
    html = '<table>'
    for row in rows:
        html += '<tr>'
        for col in row:
            html += '<td>{}</td>'.format(col)
        html += '</tr>'
    html += '</table>'
    return html

@app.route('/table/<table>/<id>')
def row(table, id):
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, id))
    row = cursor.fetchone()
    html = '<table>'
    html += '<tr>'
    for col in row:
        html += '<td>{}</td>'.format(col)
    html += '</tr>'
    html += '</table>'
    return html

# Start the web server
if __name__ == '__main__':
    app.run()










