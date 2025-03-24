from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world(): # ффункция-обработчик, вызванная при запросе URL корневого 
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True) 