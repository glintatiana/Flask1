from flask import Flask, request
import random
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.json.ensure_ascii = False

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db" # <- тут путь к БД

field_dict = ['id', 'author', 'text', 'rating']
valid_rating = [i for i in range(1,6)]


@app.route("/quotes")
def my_quotes():
    connection = sqlite3.connect(path_to_db)

    cursor = connection.cursor()
    cursor.execute("SELECT * from quotes")
    quotes_db = cursor.fetchall() #get list[tuple]
    cursor.close()
    connection.close()

    # подготовка данных - нужен список словарей
    # нужно преобразовать список кортежей в список словарей
    keys = ("id", "author", "text")
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)

    return quotes, 200

def get_quote_by_id(quote_id):
    """
    Метод для получения цитаты по ID - возвращаем объект целиком
    """
    for q in quotes:
        if q['id'] == quote_id:
            return q
    return {}

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
        cnt_obj = {"count": len(quotes)}
        return cnt_obj
    return f"Page not found", 404

@app.route("/quotes/rand")
def show_rand_quote():
    """
    Возвращаем рандомную цитату по URL /quotes/rand
    """
    return random.choice(quotes)

def fn_get_new_quote_id():
    """
    Метод для генерации свежего ID с условием, что максимальный всегда в конце списка
    """
    return quotes[-1]['id']+1

@app.route("/quotes", methods=['POST'])
def create_quote():
    """
    Метод для создания новой цитаты в справочнике цитат через POST
    реализована функция fn_get_new_quote_id для генерации нового id под новую цитату

    Возвращается создаваемый объект
    """
    data = request.json
    data['id'] = fn_get_new_quote_id()
    # выставляем дефолтное значение для рейтинга, если не задан 
    # или если задан некорректный
    if 'rating' not in data.keys() or data['rating'] not in valid_rating:
        data['rating'] = 1

    # проверяем, все ли ключи - валидные
    for key in data:
        if key not in field_dict:
            return f"Quote key '{key}' is not valid", 400 

    quotes.append(data)
    return data, 201

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    """
    Метод для изменения цитаты в словаре черех put
    """
    new_data = request.json
    
    quote = get_quote_by_id(quote_id)
    if not quote:
        return f"Quote with id={quote_id} not found", 404
    else:
        for key in new_data: # итерируем по всем возможным полям
            if key not in field_dict:
               return f"Quote key '{key}' not found", 400 
            if key == 'id':
               return f"Quote key '{key}' could not be changed", 400
            # подменяем значение, если пользователь хотит изменить на невалидный рейтинг
            if key == 'rating' and new_data['rating'] not in valid_rating:
               new_data['rating'] = 1
            quote[key] = new_data[key] # создали тут объект со всеми изменениями 
    #т теперь подменяем цитату в словаре
    for i, q in enumerate(quotes):
        if q['id'] == quote_id:
            quotes[i] = quote
            return quote, 200
    return 'Something gone wrong', 500

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    """
    Метод для удаления цитаты из списка по её ID через DELETE 
    """
    for quote in quotes:
        if quote['id'] == quote_id:
            quotes.remove(quote)
            return f"Quote with id {quote_id} is deleted.", 200
    return f"Quote with id={quote_id} not found", 404


@app.route('/filter', methods=['GET'])
def my_filter():
    """
    Метод для фильтрации цитат, вовращает массив всех цитат, подходящих под условие поиска
    """
    args = request.args
    quote_list = []

    for key in args: # итерируем по всем полям фильтрации
        if key not in field_dict:
            return f"Quote key '{key}' not found", 400
    # на этом этапе мы определили, что все ключи из запроса - ок 
    # проверяем каждую цитату на соответствие
    def flt(quote):
        for key in args:
            if str(quote[key]) != str(args[key]):
                return False
        return True
    
    quote_list = list(filter(flt, quotes))

    return quote_list, 200

if __name__ == "__main__":
    app.run(debug=True) 