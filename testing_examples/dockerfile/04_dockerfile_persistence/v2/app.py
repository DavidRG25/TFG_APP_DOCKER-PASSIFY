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

    html = "<div style='background: black; color: white; padding: 20px; font-family: monospace;'>"
    html += "<h1>Versión 2: Modo Oscuro (Mismos Datos)</h1>"
    html += "<form method='POST'><input type='text' name='item' style='padding:10px;'><button type='submit' style='background:red; color:white; border:none; padding:10px; margin-left:10px;'>Añadir al TXT</button></form>"
    html += "<h2 style='color:red;'>Archivo de Texto Persistente:</h2><ul>"
    for i in items:
        html += f"<li>{i.strip()}</li>"
    html += "</ul></div>"
    return html

if __name__ == '__main__':
    os.makedirs('/app/data', exist_ok=True)
    app.run(host='0.0.0.0', port=8080)
