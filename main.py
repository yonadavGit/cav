import mysql
import mysql.connector as sql
import http.server
import socketserver
from flask import Flask, render_template
import jinja2

page_title = "Converse about the Verse"

# Connect to the MySQL database
cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='converseabouttheverse')
cursor = cnx.cursor()

# Create the Flask app
app = Flask(__name__, template_folder='templates')


# Define the request handlers


def get_all_translations_names():
    cursor.execute('SELECT version FROM bible_version_key WHERE version IS NOT NULL;'.format())
    q = cursor.fetchall()
    trans_names = [trans[0] for trans in q]
    return trans_names


all_translations_names = get_all_translations_names()


def get_all_book_names():
    cursor.execute('SELECT n FROM key_english WHERE n IS NOT NULL;'.format())
    q = cursor.fetchall()
    book_names = [book[0] for book in q]
    return book_names


all_book_titles = get_all_book_names()


def book_id_to_title(bookId):
    cursor.execute('SELECT n FROM key_english WHERE b = {} AND n IS NOT NULL;'.format(bookId))
    title = cursor.fetchall()
    return title[0][0]


def book_title_to_id(bookTitle):
    return all_book_titles.index(bookTitle) + 1


def translation_name_to_id(translation):
    return all_translations_names.index(translation) + 1


@app.route('/liked/<_user>/<table>/')
def liked_verses(_user, table):
    # if table[0 : 1] != 't_' :
    #     table = str(translation_name_to_id(table))
    # if not book_no.isnumeric():
    #     book_no = str(book_title_to_id(book_no))
    cursor.execute('SELECT * FROM {} WHERE id IN (SELECT id_verse FROM likes WHERE user="{}");'.format(table, _user))
    rows = cursor.fetchall()
    return render_template('/table_book.html', title=page_title, rows=rows, book_title="verses liked by " + _user,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/search/<table>/<word>')
def search(table, word):
    cursor.execute('SELECT * FROM {} WHERE t LIKE "%{}%";'.format(table, word))
    rows = cursor.fetchall()
    return render_template('/table_book.html', title=page_title, rows=rows,
                           book_title='Search results for: "' + word + '"',
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>')
def table_book(table, book_no):
    # if table[0 : 1] != 't_' :
    #     table = str(translation_name_to_id(table))
    if not book_no.isnumeric():
        book_no = str(book_title_to_id(book_no))
    cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, book_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/liked/<table>/<book_no>')
def liked_verses_by_book(table, book_no):
    book_title = book_id_to_title(book_no)
    cursor.execute('SELECT * FROM {} WHERE b={} AND id IN (SELECT id_verse FROM likes);'.format(table, book_no))

    rows = cursor.fetchall()
    return render_template('/table_book.html', title=page_title, rows=rows,
                           book_title="verses liked in book " + book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


#
# SELECT n, COUNT (*) AS num_of_comments FROM Comment AS c JOIN (SELECT TNC. ID,
# key_english.n FROM TNC JOIN key_english ON TNC.b = key_english.b)
# ON c. Verse_ID = TNC. ID
# WHERE Comment_text IS NOT NULL GROUP BY key_english.n;
@app.route('/liked/amount/<table>')
def num_likes_by_book(table):
    cursor.execute('SELECT n, COUNT(*) FROM (({} AS bible JOIN likes ON bible.id = likes.id_verse ) JOIN key_english ON bible.b = key_english.b ) GROUP BY key_english.n  ;'.format(table))
    rows = cursor.fetchall()
    return render_template('/table_book_amount.html', title=page_title, rows=rows, book_title="likes per book",
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>/<chapter_no>')
def table_book_chapter(table, book_no, chapter_no):
    if table[0: 2] != 't_':
        table = str(translation_name_to_id(table))

    if not book_no.isnumeric():
        book_no = str(book_title_to_id(book_no))
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND c = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>/<chapter_no>/<verse_no>')
def table_book_chapter_verse(table, book_no, chapter_no, verse_no):
    # Query the MySQL database and generate the HTML table
    cursor.execute(
        'SELECT * FROM {} WHERE b = {} AND c = {} AND v = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no,
                                                                                        verse_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    rows_len = len(rows)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names, len=rows_len)


@app.route('/like/<table>/<book_no>/<chapter_no>/<verse_no>')
def verse_like(table, book_no, chapter_no, verse_no):
    # Query the MySQL database and generate the HTML table
    cursor.execute(
        'SELECT * FROM {} WHERE b = {} AND c = {} AND v = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no,
                                                                                        verse_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    rows_len = len(rows)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names, len=rows_len)


@app.route('/login')
def sign_in():
    return render_template('/login.html', title=page_title)


@app.route('/sign_up')
def sign_up():
    return render_template('/sign_up.html', title=page_title)


# Start the web server
if __name__ == '__main__':
    app.run()
