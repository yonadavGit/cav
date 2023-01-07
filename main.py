import mysql
import mysql.connector as sql
import http.server
import socketserver
from flask import Flask, render_template
import jinja2

# Connect to the MySQL database
cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='converseabouttheverse')
cursor = cnx.cursor()

# Create the Flask app
app=Flask(__name__,template_folder='templates')


# Define the request handlers
# @app.route('/table/<table>')
# def table(table):
#     cursor.execute('SELECT * FROM {} WHERE AND t IS NOT NULL;'.format(table))
#     rows = cursor.fetchall()
#
#     return render_template('/table_book.html', title='My Page', rows=rows)
def get_all_book_names():
    cursor.execute('SELECT n FROM key_english WHERE n IS NOT NULL;'.format())
    q = cursor.fetchall()
    book_names = [book[0] for book in q]
    print(book_names)
    return book_names

all_book_titles = get_all_book_names()

@app.route('/table/<table>/<book_no>')
def table_book(table, book_no):
    cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, book_no))
    rows = cursor.fetchall()
    book_title = bookId_to_title(book_no)
    return render_template('/table_book.html', title='My Page', rows=rows,book_title=book_title, all_book_titles = all_book_titles)



@app.route('/table/<table>/<book_no>/<chapter_no>')
def table_book_chapter(table, book_no, chapter_no):
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND c = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no))
    rows = cursor.fetchall()
    book_title = bookId_to_title(book_no)
    return render_template('/table_book.html', title='My Page', rows=rows, book_title=book_title)


@app.route('/table/<table>/<book_no>/<chapter_no>/<verse_no>')
def table_book_chapter_verse(table, book_no, chapter_no, verse_no):
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND c = {} AND v = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no, verse_no))
    rows = cursor.fetchall()
    book_title = bookId_to_title(book_no)
    return render_template('/table_book.html', title='My Page', rows=rows, book_title=book_title)


# @app.route('/table/<table>/<id>')
# def row(table, id):
#     # Query the MySQL database and generate the HTML table
#     cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, id))
#     row = cursor.fetchone()
#     html = '<table>'
#     html += '<tr>'
#     for col in row:
#         html += '<td>{}</td>'.format(col)
#     html += '</tr>'
#     html += '</table>'
#     return html


def bookId_to_title(bookId):
    cursor.execute('SELECT n FROM key_english WHERE b = {} AND n IS NOT NULL;'.format(bookId))
    title = cursor.fetchall()
    return title[0][0]



# Start the web server
if __name__ == '__main__':
    get_all_book_names()
    app.run()
