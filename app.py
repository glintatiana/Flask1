from flask import Flask, request
import random



app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/")
def hello_world():
    """
    Обработчик для корневого URL 
    """
    return "Hello, World!"

about_me = {
    "name": "Татьяна",
    "surname": "Глинская",
    "email": "glintatiana@gmail.com"
}

@app.route("/about")
def about():
    """
    Информация по URL /about
    """
    return about_me

quotes = [
    {
    "id": 3,
    "author": "Rick Cook",
    "text": """Программирование сегодня — это гонка
    разработчиков программ, стремящихся писать программы с
    большей и лучшей идиотоустойчивостью, и вселенной, которая
    пытается создать больше отборных идиотов. Пока вселенная
    побеждает."""
    },
    {
    "id": 5,
    "author": "Waldi Ravens",
    "text": """Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в
    руках."""
    },
    {
    "id": 6,
    "author": "Mosher’s Law of Software Engineering",
    "text": """Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."""
    },
    {
    "id": 8,
    "author": "Yoggi Berra",
    "text": """В теории, теория и практика неразделимы. На практике это не так."""
    },
]

field_dict = ['id', 'author', 'text']

@app.route("/quotes")
def my_quotes():
    """
    Возвращает все цитаты по URL /quotes
    """
    return quotes

def get_quote_by_id(quote_id):
    """
    Метод для получения цитаты по ID - возвращаем объект целиком (Практика часть 2 пункт 3)
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
    return quotes[-1]['id']+1

@app.route("/quotes", methods=['POST'])
def create_quote():
    """
    метод для создания новой цитаты в справочнике цитат через POST (Практика часть 2 пункт 1)
    реализована функция fn_get_new_quote_id для генерации нового id под новую цитату

    возвращается создаваемый объект (Практика часть 2 пункт 2)
    """
    data = request.json
    data['id'] = fn_get_new_quote_id()
    quotes.append(data)
    return data, 201

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(id):
    new_data = request.json
    quote = get_quote_by_id(new_data['id'])
    if quote == {}:
        return f"Quote with id={new_data['id']} not found", 404
    else:
        for j in new_data: # итерируем по всем возможным полям
            if j not in field_dict:
               return f"Quote key "{j}" not found", 404 
             
        return quote, 200


if __name__ == "__main__":
    app.run(debug=True) 