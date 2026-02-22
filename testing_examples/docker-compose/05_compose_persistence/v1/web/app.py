from flask import Flask, request, render_template_string, redirect
import redis
import os

app = Flask(__name__)
db = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web V1 (Diseño Azul)</title>
    <style>
        body { font-family: Arial; background-color: #e3f2fd; padding: 50px; text-align: center; }
        .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        h1 { color: #1565c0; }
        ul { list-style-type: none; padding: 0; }
        li { background: #bbdefb; margin: 5px 0; padding: 10px; border-radius: 5px; }
        input[type="text"] { padding: 10px; width: 70%; border: 1px solid #90caf9; border-radius: 5px; }
        button { padding: 10px 15px; background: #1976d2; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Diseño V1 (Azul)</h1>
        <form method="POST">
            <input type="text" name="item" placeholder="Nuevo dato..." required>
            <button type="submit">Añadir</button>
        </form>
        <h3>Datos en Base de Datos (Redis):</h3>
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
