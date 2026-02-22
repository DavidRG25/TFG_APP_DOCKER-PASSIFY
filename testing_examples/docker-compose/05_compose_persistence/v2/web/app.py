from flask import Flask, request, render_template_string, redirect
import redis
import os

app = Flask(__name__)
db = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web V2 (Diseño Verde)</title>
    <style>
        body { font-family: 'Courier New', Courier, monospace; background-color: #e8f5e9; padding: 50px; text-align: center; }
        .box { background: white; padding: 30px; border: 4px dashed #4caf50; max-width: 500px; margin: auto; }
        h1 { color: #2e7d32; text-transform: uppercase; }
        ul { list-style-type: square; text-align: left; }
        li { background: #c8e6c9; margin: 8px 0; padding: 12px; font-weight: bold; }
        input[type="text"] { padding: 12px; width: 60%; border: 2px solid #81c784; }
        button { padding: 12px 20px; background: #388e3c; color: white; border: none; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🔥 Diseño V2 (Verde) 🔥</h1>
        <p>¡Hemos actualizado la web pero los datos deben seguir aquí!</p>
        <form method="POST">
            <input type="text" name="item" placeholder="Añadir algo más..." required>
            <button type="submit">GUARDAR</button>
        </form>
        <h3>Tus Datos Intactos:</h3>
        <ul>
            {% for item in items %}
                <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form.get('item')
        if item:
            db.lpush('mis_datos', item)
        return redirect('/')
    
    items = db.lrange('mis_datos', 0, -1)
    return render_template_string(TEMPLATE, items=items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
