from flask import Flask, request
import random

app = Flask(__name__)
app.json.ensure_ascii = False

about_me = {
    "name": "Татьяна",
    "surname": "Глинская",
    "email": "glintatiana@gmail.com"
}

quotes = [
    {
    "id": 3,
    "author": "Rick Cook",
    "text": """Программирование сегодня — это гонка
    разработчиков программ, стремящихся писать программы с
    большей и лучшей идиотоустойчивостью, и вселенной, которая
    пытается создать больше отборных идиотов. Пока вселенная
    побеждает.""",
    "rating" : 2
    },
    {
    "id": 5,
    "author": "Waldi Ravens",
    "text": """Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в
    руках.""",
    "rating" : 3
    },
    {
    "id": 6,
    "author": "Mosher’s Law of Software Engineering",
    "text": """Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.""",
    "rating" : 4
    },
    {
    "id": 8,
    "author": "Yoggi Berra",
    "text": """В теории, теория и практика неразделимы. На практике это не так.""",
    "rating" : 5
    },
]

field_dict = ['id', 'author', 'text', 'rating']
valid_rating = [i for i in range(1,6)]

@app.route("/")
def hello_world():
    """
    Обработчик для корневого URL 
    """
    return "Hello, World!"

@app.route("/about")
def about():
    """
    Информация по URL /about
    """
    return about_me


@app.route("/quotes")
def my_quotes():
    """
    Возвращает все цитаты по URL /quotes
    """
    return quotes

def get_quote_by_id(quote_id):
    """
    Метод для получения цитаты по ID - возвращаем объект целиком
    """
    for i in quotes:
        if i['id'] == quote_id:
            return i
    return {}

@app.route("/quotes/<int:quote_id>")
def show_quote(quote_id):
    """
    Метод для динамического задания номера цитаты через URL /quites/номер_цитаты
    Если цитаты нет - возвращаем 404 
    """
    ans = get_quote_by_id(quote_id)
    if ans == {}:
        return f"Quote with id={quote_id} not found", 404
    else:
        return ans

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
    for i in data:
        if i not in field_dict:
            return f"Quote key '{i}' is not valid", 400 

    quotes.append(data)
    return data, 201

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    """
    Метод для изменения цитаты в словаре черех put
    """
    new_data = request.json
    
    quote = get_quote_by_id(quote_id)
    if quote == {}:
        return f"Quote with id={quote_id} not found", 404
    else:
        for j in new_data: # итерируем по всем возможным полям
            if j not in field_dict:
               return f"Quote key '{j}' not found", 400 
            if j == 'id':
               return f"Quote key '{j}' could not be changed", 400
            # подменяем значение, если пользователь хотит изменить на невалидный рейтинг
            if j == 'rating' and new_data['rating'] not in valid_rating:
               new_data['rating'] = 1
            quote[j] = new_data[j] # создали тут объект со всеми изменениями 
    #т теперь подменяем цитату в словаре
    for i, v in enumerate(quotes):
        if v['id'] == quote_id:
            quotes[i] = quote
            return quote, 200
    return 'Something gone wrong', 500

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    """
    Метод для удаления цитаты из списка по её ID через DELETE 
    """
    quote = get_quote_by_id(quote_id)
    if quote == {}:
        return f"Quote with id={quote_id} not found", 404
    for i, v in enumerate(quotes):
        if v['id'] == quote_id:
            quotes.pop(i)
            return f"Quote with id {quote_id} is deleted.", 200
    return 'Something gone wrong', 500


if __name__ == "__main__":
    app.run(debug=True) 