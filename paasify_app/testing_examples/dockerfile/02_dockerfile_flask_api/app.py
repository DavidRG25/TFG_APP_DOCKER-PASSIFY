from flask import Flask, jsonify, render_template_string
import os
import datetime
import socket

app = Flask(__name__)

# Diseño premium directamente en el código para facilitar el despliegue de un solo archivo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PaaSify Cloud Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex items-center justify-center p-6">
    <div class="max-w-4xl w-full">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-8 mb-8 shadow-2xl shadow-blue-200 text-white relative overflow-hidden">
            <div class="relative z-10">
                <div class="flex items-center gap-3 mb-2">
                    <span class="bg-blue-400/30 p-2 rounded-lg backdrop-blur-sm">
                        <i class="fas fa-server"></i>
                    </span>
                    <h1 class="text-3xl font-bold">Cloud Service Online</h1>
                </div>
                <p class="text-blue-100 opacity-90">Este contenedor está siendo orquestado por PaaSify.</p>
            </div>
            <!-- Círculos decorativos -->
            <div class="absolute -right-20 -top-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            <div class="absolute right-20 -bottom-20 w-48 h-48 bg-blue-400/20 rounded-full blur-2xl"></div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div class="text-slate-400 text-sm font-semibold uppercase mb-2">Host Name</div>
                <div class="text-slate-800 text-xl font-bold flex items-center gap-2">
                    <i class="fas fa-network-wired text-blue-500"></i>
                    {{ hostname }}
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div class="text-slate-400 text-sm font-semibold uppercase mb-2">Node Version</div>
                <div class="text-slate-800 text-xl font-bold flex items-center gap-2">
                    <i class="fab fa-python text-blue-400"></i>
                    Python 3.9
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div class="text-slate-400 text-sm font-semibold uppercase mb-2">Server Time</div>
                <div class="text-slate-800 text-xl font-bold flex items-center gap-2">
                    <i class="far fa-clock text-indigo-500"></i>
                    {{ time }}
                </div>
            </div>
        </div>

        <!-- System Info -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                <h2 class="font-bold text-slate-800 flex items-center gap-2">
                    <i class="fas fa-microchip text-slate-400"></i>
                    System Information
                </h2>
                <span class="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    Stable
                </span>
            </div>
            <div class="p-6">
                <div class="space-y-4">
                    <div class="flex justify-between items-center p-3 hover:bg-slate-50 rounded-xl transition-colors">
                        <span class="text-slate-500">OS Platform</span>
                        <span class="font-mono text-slate-800 font-bold">Linux (Docker Optimized)</span>
                    </div>
                    <div class="flex justify-between items-center p-3 hover:bg-slate-50 rounded-xl transition-colors">
                        <span class="text-slate-500">Container ID</span>
                        <span class="font-mono text-blue-600 bg-blue-50 px-2 py-1 rounded">f7a9d2c1...</span>
                    </div>
                    <div class="flex justify-between items-center p-3 hover:bg-slate-50 rounded-xl transition-colors">
                        <span class="text-slate-500">Uptime</span>
                        <span class="text-slate-800 font-bold">99.9% Reliable</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <p class="text-center mt-8 text-slate-400 text-sm">
            &copy; 2026 PaaSify Dashboard &bull; Prototipo de TFG de David
        </p>
    </div>
</body>
</html>
"""

@app.get('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        time=datetime.datetime.now().strftime("%H:%M:%S"),
        hostname=socket.gethostname()
    )

@app.get('/api/status')
def status():
    return jsonify({
        "status": "online",
        "message": "API de consulta horaria y sistema",
        "version": "1.0.0",
        "env": os.environ.get('APP_ENV', 'development'),
        "hostname": socket.gethostname()
    })

@app.get('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
