from flask import Flask

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/")
def hello_world(): # ффункция-обработчик, вызванная при запросе URL корневого 
    return "Hello, World!"

about_me = {
    "name": "Татьяна",
    "surname": "Глинская",
    "email": "glintatiana@gmail.com"
}

@app.route("/about")
def about():
    return about_me

if __name__ == "__main__":
    app.run(debug=True) 