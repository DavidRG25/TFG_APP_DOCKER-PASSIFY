from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import redis
import psycopg2
import datetime
import time
import sys

app = Flask(__name__)
CORS(app)

# Configuración Redis
cache = redis.Redis(host=os.environ.get('REDIS_HOST', 'cache-layer'), port=6379, decode_responses=True)

def log_message(msg):
    """Printea con flush para asegurar que salga en los logs de Docker inmediatamente."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr, flush=True)

def get_db_connection():
    return psycopg2.connect(
        host='postgres-db',
        database='postgres',
        user='postgres',
        password=os.environ.get('POSTGRES_PASSWORD', 'passify_secret'),
        connect_timeout=5
    )

def ensure_table_exists():
    """Intenta crear la tabla si no existe. Robusto ante fallos de conexión inicial."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS test_data (id serial PRIMARY KEY, content text, created_at timestamp);')
        conn.commit()
        cur.close()
        log_message("[DB] Tabla 'test_data' verificada/creada correctamente.")
    except Exception as e:
        log_message(f"[DB] Postgres no está listo todavía: {e}")
    finally:
        if conn:
            conn.close()

@app.route('/')
def hello():
    ensure_table_exists()
    try:
        hits = cache.incr('hits')
    except Exception:
        hits = "Error"
    return jsonify({"status": "online", "hits": hits, "service": "api-backend"})

@app.route('/api/save', methods=['POST'])
def save_data():
    ensure_table_exists()
    data = request.json.get('content', '')
    if not data:
        return jsonify({"error": "No content provided"}), 400

    log_message(f"[PIPELINE] Mensaje recibido en API: '{data}'")
    results = {}
    
    # 1. PostgreSQL
    try:
        log_message("[DB] Intentando persistir en PostgreSQL...")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO test_data (content, created_at) VALUES (%s, %s)',
                    (data, datetime.datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        log_message("[DB] ✓ Datos guardados en Postgres.")
        results['postgres'] = "✓ Guardado OK"
    except Exception as e:
        log_message(f"[DB] ✗ Error en Postgres: {str(e)}")
        results['postgres'] = f"✗ Error: {str(e)}"

    # 2. Redis
    try:
        log_message("[CACHE] Intentando registrar en Redis Historial...")
        cache.lpush('history', data)
        cache.ltrim('history', 0, 4)
        log_message("[CACHE] ✓ Historial actualizado en Redis.")
        results['redis'] = "✓ Cacheado OK"
    except Exception as e:
        log_message(f"[CACHE] ✗ Error en Redis: {str(e)}")
        results['redis'] = f"✗ Error: {str(e)}"

    return jsonify({"message": "Proceso completado", "results": results})

@app.route('/api/stats')
def get_stats():
    ensure_table_exists()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM test_data;')
        db_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        history = cache.lrange('history', 0, -1)
        return jsonify({
            "total_db_records": db_count, 
            "recent_history": history,
            "redis_hits": cache.get('hits')
        })
    except Exception as e:
        return jsonify({"total_db_records": 0, "recent_history": [], "error": str(e)})

if __name__ == '__main__':
    log_message("=== Iniciando API-BACKEND del Mega Stack ===")
    time.sleep(2)
    ensure_table_exists()
    app.run(host='0.0.0.0', port=5000)
