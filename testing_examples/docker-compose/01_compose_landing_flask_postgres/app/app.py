import os
import psycopg2
from flask import Flask, request, redirect, render_template_string

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "paasify")
DB_USER = os.getenv("DB_USER", "paasify")
DB_PASSWORD = os.getenv("DB_PASSWORD", "paasify")

TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>PaaSify - Compose + DB</title>
  <style>
    *{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Arial,sans-serif;background:#f6f7fb;color:#111827}
    .container{max-width:920px;margin:0 auto;padding:24px}
    .hero,.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:18px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
    .hero h1{margin:0 0 6px 0;font-size:28px}
    .muted{color:#6b7280}
    form{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
    input{flex:1;min-width:240px;padding:10px 12px;border:1px solid #e5e7eb;border-radius:10px}
    button{border:0;border-radius:10px;padding:10px 14px;background:#2563eb;color:#fff;font-weight:600;cursor:pointer}
    table{width:100%;border-collapse:collapse;margin-top:12px}
    th,td{padding:10px;border-bottom:1px solid #e5e7eb;text-align:left}
    .row{display:grid;grid-template-columns:1fr;gap:14px;margin-top:14px}
    @media (min-width:900px){.row{grid-template-columns:1fr 1fr}}
    code{background:#f3f4f6;padding:2px 6px;border-radius:8px}
  </style>
</head>
<body>
  <main class="container">
    <section class="hero">
      <h1>Landing con persistencia (Docker Compose)</h1>
      <p class="muted">Guarda mensajes en Postgres usando un volumen. Útil para testings “realistas”.</p>
      <p class="muted">Healthcheck: <code>/healthz</code></p>
      <form method="post" action="/submit">
        <input name="message" placeholder="Escribe un mensaje (se guardará en DB)" maxlength="200" required />
        <button type="submit">Guardar</button>
      </form>
    </section>

    <div class="row">
      <section class="card">
        <h2 style="margin-top:0">Mensajes guardados</h2>
        <table>
          <thead><tr><th>ID</th><th>Mensaje</th><th>Creado</th></tr></thead>
          <tbody>
            {% for r in rows %}
              <tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td class="muted">{{ r[2] }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </section>

      <section class="card">
        <h2 style="margin-top:0">Detalles de conexión</h2>
        <ul class="muted">
          <li>Host: <code>{{ db_host }}</code></li>
          <li>DB: <code>{{ db_name }}</code></li>
          <li>User: <code>{{ db_user }}</code></li>
          <li>Port: <code>{{ db_port }}</code></li>
        </ul>
        <p class="muted">Para validar persistencia, guarda un mensaje, haz <code>docker compose down</code> y luego <code>up</code> de nuevo: los datos deben seguir.</p>
      </section>
    </div>
  </main>
</body>
</html>"""


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


app = Flask(__name__)


@app.get("/healthz")
def healthz():
    # Comprueba conectividad DB
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "detail": str(e)}, 500


@app.get("/")
def index():
    init_db()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, message, created_at FROM messages ORDER BY id DESC LIMIT 50;")
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template_string(
        TEMPLATE,
        rows=rows,
        db_host=DB_HOST,
        db_name=DB_NAME,
        db_user=DB_USER,
        db_port=DB_PORT,
    )


@app.post("/submit")
def submit():
    msg = (request.form.get("message") or "").strip()
    if not msg:
        return redirect("/")
    init_db()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (message) VALUES (%s);", (msg,))
        conn.commit()
    finally:
        conn.close()
    return redirect("/")
