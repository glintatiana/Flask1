from flask import Flask, request
import random
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.json.ensure_ascii = False

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "sqlite_example/store.db" # <- тут путь к БД

field_dict = ['id', 'author', 'text', 'rating']
valid_rating = [i for i in range(1,6)]

print(path_to_db)

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


print(quotes)