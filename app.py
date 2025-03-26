from flask import Flask, request, g
from pathlib import Path

#sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

import random
import sqlite3

class Base(DeclarativeBase):
    pass


BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "sqlite_example/store.db" # <- тут путь к БД

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))
    rating : Mapped[int] = mapped_column(default = 1)

    def __init__(self, author, text, rating = 1):
        self.author = author
        self.text = text

    def to_dict(self):
        return {
            "id" : self.id,
            "author" : self.author,
            "text" : self.text,
            "rating" : self.rating
        }


field_dict = ['id', 'author', 'text', 'rating']



@app.route("/quotes")
def my_quotes():
    """
    Метод возвращает список всех цитат
    Чтение идет из бд sqlite 
    """
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = [q.to_dict() for q in quotes_db]

    return quotes, 200

@app.route("/quotes/<int:quote_id>")
def show_quote(quote_id):
    """
    Метод для динамического задания номера цитаты через URL /quites/номер_цитаты
    Если цитаты нет - возвращаем 404 
    """

    quote = db.one_or_404(db.select(QuoteModel).filter_by(id=quote_id))

    return quote.to_dict(), 200

@app.route("/quotes/<path:subpath>")
def show_quote_count(subpath):
    """
    Метод для тестирования указания динамического URL 
    Обрабатывает /count 
    """
    if subpath == 'count':
        quotes_db = db.session.scalars(db.select(QuoteModel)).all()

        return  {"count": len(quotes_db)}, 200
    return f"Page not found", 503

@app.route("/quotes", methods=['POST'])
def create_quote():
    """
    Метод для создания новой цитаты в справочнике цитат через POST
    Возвращается создаваемый объект
    """
    data = request.json

    rating_norm = data.get('rating')
    if rating_norm is None or rating_norm not in range(1,6):
        rating_norm = 1

    quote = QuoteModel(data.get('author'), data.get('text'), rating_norm)
    db.session.add(quote)
    db.session.commit()

    return db.session.get(QuoteModel, quote.id).to_dict(), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    """
    Метод для изменения цитаты в словаре черех put
    """
    new_data = request.json

    rating_norm = new_data.get('rating')
    if rating_norm is None or rating_norm not in range(1,6):
        rating_norm = 1

    quote = db.get_or_404(QuoteModel, quote_id)

    if quote and not (set(new_data.keys()) - set (('author','text', 'rating'))):
        if 'author' in new_data.keys():
            quote.author = new_data.get('author')
        if 'text' in new_data.keys():
            quote.text = new_data.get('text')
        if 'rating' in new_data.keys():
            quote.rating = rating_norm

    db.session.commit()

    return quote.to_dict(), 200 


@app.route('/filter', methods=['GET'])
def my_filter():
    """
    Метод для фильтрации цитат, вовращает массив всех цитат, подходящих под условие поиска
    """
    args = request.args
    print(args)

    for key in args: # итерируем по всем полям фильтрации
         if key not in field_dict:
             return f"Quote key '{key}' not found", 400

    # quotes = db.session.query(QuoteModel).filter_by(**request.args).all()
    quotes = db.session.scalars(db.select(QuoteModel).filter_by(**request.args)).all()

    return [q.to_dict() for q in quotes], 200

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    """
    Метод для удаления цитаты из списка по её ID через DELETE 
    """

    quote = db.get_or_404(QuoteModel, quote_id)

    db.session.delete(quote)

    try:
        db.session.commit()
        return f"Quote with id {quote_id} is deleted.", 200
    except Exception as e:
        db.session.rollback()
        return f"Database error: {e.description}", 503
    
if __name__ == "__main__":
    app.run(debug=True) 