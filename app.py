from flask import Flask, request, g
import random
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.json.ensure_ascii = False

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "sqlite_example/store.db" # <- тут путь к БД

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


field_dict = ['id', 'author', 'text', 'rating']

def tuple_to_dict(keys, tuple_list):
    """
    Метод для преобразования списка кортежей в список словарей
    На вход - ключи + список кортежей 
    """
    dict_list = []
    for dict_ in tuple_list:
        dict_l = dict(zip(keys, dict_))
        dict_list.append(dict_l)
    
    return dict_list

def get_quote_by_id(quote_id):
    """
    Метод для получения цитаты по ID - возвращаем объект целиком
    """

    cursor = get_db().cursor()
    quote = cursor.execute("SELECT * from quotes where id = ?", (quote_id,)).fetchone()
    
    # для обработчиков на пустое 
    if quote:
        keys = ("id", "author", "text", "rating")
        quote_dict = tuple_to_dict(keys, (quote,)) # преобразуем в tuple, так как возвращается только одна строка 
        return quote_dict
    return {}

@app.route("/quotes")
def my_quotes():
    """
    Метод возвращает список всех цитат
    Чтение идет из бд sqlite 
    """
    cursor = get_db().cursor()
    cursor.execute("SELECT * from quotes")
    quotes_db = cursor.fetchall()

    # подготовка данных - нужен список словарей
    # нужно преобразовать список кортежей в список словарей
    keys = ("id", "author", "text", "rating")
    quotes = tuple_to_dict(keys, quotes_db)

    return quotes, 200

@app.route("/quotes/<int:quote_id>")
def show_quote(quote_id):
    """
    Метод для динамического задания номера цитаты через URL /quites/номер_цитаты
    Если цитаты нет - возвращаем 404 
    """
    ans = get_quote_by_id(quote_id)
    if ans:
        return ans
    else:
        return f"Quote with id={quote_id} not found", 404

@app.route("/quotes/<path:subpath>")
def show_quote_count(subpath):
    """
    Метод для тестирования указания динамического URL 
    Обрабатывает /count 
    """
    if subpath == 'count':
        cursor = get_db().cursor()
        cursor.execute("SELECT count(1) from quotes")
        quotes_cnt = cursor.fetchone() #get list[tuple]

        return  {"count": quotes_cnt[0]}, 200
    return f"Page not found", 503

@app.route("/quotes", methods=['POST'])
def create_quote():
    """
    Метод для создания новой цитаты в справочнике цитат через POST
    Возвращается создаваемый объект
    """
    data = request.json

    # проверяем, все ли ключи - валидные
    for key in data:
        if key not in field_dict:
            return f"Quote key '{key}' is not valid", 400 

    cursor = get_db().cursor()

    rating_norm = data.get('rating')
    if rating_norm is None or rating_norm not in range(1,6):
        rating_norm = 1
    cursor.execute("insert into quotes (author, text, rating) values (?,?,?)",(data.get('author'), data.get('text'), rating_norm))
    rowid = cursor.lastrowid

    connection.commit()
  
    cursor.execute("SELECT * from quotes where rowid = ?", (rowid,))
    quote = cursor.fetchall() #get list[tuple]


    keys = ("id", "author", "text", "rating")
    quote_list = tuple_to_dict(keys, quote)

    return quote_list, 201

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    """
    Метод для изменения цитаты в словаре черех put
    """
    new_data = request.json

    cursor = get_db.cursor()
    new_quote_data = (new_data.get('author'), new_data.get('text'))    
    update_quote = "UPDATE quotes SET author=coalesce(?, author), text=coalesce(?, text) WHERE id=?"
    cursor.execute(update_quote, (*new_quote_data, quote_id))
    rowcnt = cursor.rowcount

    connection.commit()

    if rowcnt == 0:
        return f"Quote with id={quote_id} not found", 404

    return get_quote_by_id(quote_id), 200

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    """
    Метод для удаления цитаты из списка по её ID через DELETE 
    """
    cursor = get_db.cursor()
    delete_quote = "delete from quotes WHERE id=?"
    cursor.execute(delete_quote, (quote_id,))
    rowcnt = cursor.rowcount

    connection.commit()

    if rowcnt == 0:
        return f"Quote with id={quote_id} not found", 404

    return f"Quote with id {quote_id} is deleted.", 200

if __name__ == "__main__":
    app.run(debug=True) 