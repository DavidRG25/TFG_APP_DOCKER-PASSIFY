from flask import Flask, request
import os

app = Flask(__name__)
DATA_FILE = '/app/data/datos.txt'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form.get('item')
        if item:
            with open(DATA_FILE, 'a') as f:
                f.write(item + '\n')
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            items = f.readlines()
    else:
        items = []

    html = "<h1>Versión 1: Interfaz Sencilla</h1>"
    html += "<form method='POST'><input type='text' name='item'><button type='submit'>Guardar</button></form>"
    html += "<h2>Archivo de Texto Persistente:</h2><ul>"
    for i in items:
        html += f"<li>{i.strip()}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    os.makedirs('/app/data', exist_ok=True)
    app.run(host='0.0.0.0', port=8080)
