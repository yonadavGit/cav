import mysql
import mysql.connector as sql
import http.server
import socketserver
from flask import Flask, render_template, request, redirect
import jinja2

page_title = "Converse about the Verse"

# Connect to the MySQL database
cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='bibels', port=3305)
cursor = cnx.cursor()

# Create the Flask app
app = Flask(__name__, template_folder='templates')

# Define the request handlers

global_user = ''


def get_all_translations_names() :
    cursor.execute('SELECT version FROM bible_version_key WHERE version IS NOT NULL;'.format())
    q = cursor.fetchall()
    trans_names = [trans[0] for trans in q]
    return trans_names


all_translations_names = get_all_translations_names()


def size_comments() :
    cursor.execute("SELECT COUNT(*) FROM comments")
    result = cursor.fetchone()
    return result[0]


table_comments_size = size_comments()


def size_likes() :
    cursor.execute("SELECT COUNT(*) FROM likes")
    result = cursor.fetchone()
    return result[0]


table_likes_size = size_likes()


def get_all_book_names() :
    cursor.execute('SELECT n FROM key_english WHERE n IS NOT NULL;'.format())
    q = cursor.fetchall()
    book_names = [book[0] for book in q]
    return book_names


all_book_titles = get_all_book_names()


def book_id_to_title(bookId) :
    cursor.execute('SELECT n FROM key_english WHERE b = {} AND n IS NOT NULL;'.format(bookId))
    title = cursor.fetchall()
    return title[0][0]


def book_title_to_id(bookTitle) :
    return all_book_titles.index(bookTitle) + 1


def translation_name_to_id(translation) :
    return all_translations_names.index(translation) + 1


@app.route('/home/<_user>/<table>')
def liked_verses(_user, table) :
    cursor.execute('SELECT * FROM {} WHERE id IN (SELECT id_verse FROM likes WHERE user="{}");'.format(table, _user))
    rows = cursor.fetchall()
    global global_user
    global_user = _user
    return render_template('/main_page.html', title=page_title, rows=rows, book_title="verses liked by " + _user,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/search/<table>/<word>')
def search(table, word) :
    cursor.execute('SELECT * FROM {} WHERE t LIKE "%{}%";'.format(table, word))
    rows = cursor.fetchall()
    return render_template('/search_page.html', title=page_title, rows=rows,
                           book_title='Search results for: "' + word + '"',
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>')
def table_book(table, book_no) :
    if not book_no.isnumeric() :
        book_no = str(book_title_to_id(book_no))
    cursor.execute('SELECT * FROM {} WHERE b = {} AND t IS NOT NULL;'.format(table, book_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/liked/<table>/<book_no>')
def liked_verses_by_book(table, book_no) :
    book_title = book_id_to_title(book_no)
    cursor.execute('SELECT * FROM {} WHERE b={} AND id IN (SELECT id_verse FROM likes);'.format(table, book_no))

    rows = cursor.fetchall()
    return render_template('/table_book.html', title=page_title, rows=rows,
                           book_title="verses liked in book " + book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/liked/amount/<table>')
def num_likes_by_book(table) :
    cursor.execute(
        'SELECT n, COUNT(*) FROM (({} AS bible JOIN likes ON bible.id = likes.id_verse ) JOIN key_english ON bible.b = key_english.b ) GROUP BY key_english.n  ;'.format(
            table))
    rows = cursor.fetchall()
    return render_template('/table_book_amount.html', title=page_title, rows=rows, book_title="likes per book",
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>/<chapter_no>')
def table_book_chapter(table, book_no, chapter_no) :
    if table[0 : 2] != 't_' :
        table = str(translation_name_to_id(table))

    if not book_no.isnumeric() :
        book_no = str(book_title_to_id(book_no))
    # Query the MySQL database and generate the HTML table
    cursor.execute('SELECT * FROM {} WHERE b = {} AND c = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no))
    rows = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    return render_template('/table_book.html', title=page_title, rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names)


@app.route('/table/<table>/<book_no>/<chapter_no>/<verse_no>')
def userliked(table, book_no, chapter_no, verse_no) :
    cursor.execute(
        'SELECT * FROM {} WHERE b = {} AND c = {} AND v = {} AND t IS NOT NULL;'.format(table, book_no, chapter_no,
                                                                                        verse_no))
    vers = cursor.fetchall()
    book_title = book_id_to_title(book_no)
    cursor.execute(
        'SELECT user, comment FROM comments WHERE id_verse = {};'.format(vers[0][0]))
    rows = cursor.fetchall()
    return render_template('/userliked.html', title=page_title, vers=vers[0], rows=rows, book_title=book_title,
                           all_book_titles=all_book_titles, all_translations_names=all_translations_names, table=table)


@app.route('/login', methods=['GET'])
def sign_in() :
    return render_template('/login.html', title=page_title)


@app.route('/signin', methods=['POST'])
def login_action() :
    username = request.form['username']
    password = request.form['password']
    cursor.execute('SELECT * FROM users_passwords WHERE id = "{}" AND pass = "{}";'.format(username, password))
    user = cursor.fetchone()
    if user :
        global global_user
        global_user = username
        return redirect(f'/home/{username}/t_kjv')
    else :
        return redirect('/login')


@app.route('/sign_up')
def sign_up() :
    return render_template('/sign_up.html', title=page_title)


@app.route('/signup', methods=['POST'])
def save_user() :
    username = request.form['username']
    password = request.form['password']
    global global_user
    global_user = username
    # Do something with the input, such as saving it to a database
    cursor.execute('INSERT INTO users_passwords (id, pass) VALUES ("{}", "{}");'.format(username, password))
    return redirect(f'/home/{username}/t_kjv')


@app.route('/navbar', methods=['POST'])
def nav() :
    translation_ver = request.form['translation']
    cursor.execute('SELECT table_name FROM bible_version_key WHERE version = "{}";'.format(translation_ver))
    trans = cursor.fetchall()
    book_str = request.form['book']
    book = book_title_to_id(book_str)
    chapter = request.form['chapter']
    verse = request.form['verse']
    if chapter == '' :
        return redirect(f'/table/{trans[0][0]}/{book}')
    if verse == '' :
        return redirect(f'/table/{trans[0][0]}/{book}/{chapter}')
    return redirect(f'/table/{trans[0][0]}/{book}/{chapter}/{verse}')


@app.route('/likes_per_book', methods=['POST'])
def likes_per_book() :
    return redirect('/liked/amount/t_kjv')


@app.route('/liked_verse', methods=['POST'])
def liked_verse() :
    book_str = request.form['book']
    book = book_title_to_id(book_str)
    return redirect(f'/liked/t_kjv/{book}')


@app.route('/search_word', methods=['POST'])
def search_word() :
    word = request.form['word']
    return redirect(f'/search/t_kjv/{word}')


@app.route('/return_home', methods=['POST'])
def return_home() :
    return redirect(f'/home/{global_user}/t_kjv')


@app.route('/like', methods=['POST'])
def like() :
    dynamic_variable = request.form.get("my_variable")
    cursor.execute(
        'SELECT 1 FROM likes WHERE user="{}" AND id_verse = "{}" AND EXISTS (SELECT 1 FROM likes WHERE user="{}" AND id_verse = "{}");'.format(
            global_user,
            dynamic_variable, global_user, dynamic_variable))
    result = cursor.fetchone()
    if result :
        return redirect(f'/home/{global_user}/t_kjv')
    else :
        global table_likes_size
        table_likes_size += 1
        cursor.execute(
            'INSERT INTO likes (id, user, id_verse) VALUES ("{}", "{}","{}");'.format(table_likes_size, global_user,
                                                                                      dynamic_variable))
        return redirect(f'/home/{global_user}/t_kjv')


@app.route('/dislike', methods=['POST'])
def dislike() :
    cursor.execute("SELECT COUNT(*) FROM likes")
    result = cursor.fetchone()
    dynamic_variable = request.form.get("my_variable")
    cursor.execute('DELETE FROM likes WHERE user = "{}" AND id_verse = "{}";'.format(global_user, dynamic_variable))
    return redirect(f'/home/{global_user}/t_kjv')


@app.route('/post_comment', methods=['POST'])
def post_comment() :
    global table_comments_size
    table_comments_size += 1
    comment = request.form['comment']
    id_verse = request.form.get("id_verse")
    table = request.form.get("table")
    book_id = request.form.get("book_id")
    chapter_id = request.form.get("chapter_id")
    verse_id = request.form.get("verse_id")
    cursor.execute(
        'INSERT INTO comments (id, user, id_verse, comment) VALUES ("{}", "{}", "{}","{}");'.format(table_comments_size,
                                                                                                    global_user,
                                                                                                    id_verse, comment))
    return redirect(f'/table/{table}/{book_id}/{chapter_id}/{verse_id}')


# Start the web server
if __name__ == '__main__' :
    app.run()
