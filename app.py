from flask import Flask, render_template_string, request
from tests.test_smoke import smoke_test
from tests.test_integration import integration_test
from tests.test_regression import regression_test
from utils.email_utils import enviar_correo
from utils.report_utils import generar_pdf
import os
import subprocess
from datetime import datetime
import time
import threading
from tests.test_regression import regression_test

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pruebas automatizadas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 35%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #2d3748;
            position: relative;
        }
        
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.02)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.02)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.03)"/><circle cx="20" cy="80" r="0.5" fill="rgba(255,255,255,0.03)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            padding: 3rem;
            max-width: 900px;
            width: 90%;
            margin: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #2ecc71, #9b59b6);
            border-radius: 20px 20px 0 0;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #2c3e50, #34495e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.2rem;
            font-weight: 500;
        }
        
        .test-form {
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 2rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.8rem;
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.1rem;
        }
        
        .form-control {
            width: 100%;
            padding: 1rem;
            border: 2px solid #ecf0f1;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
            font-family: inherit;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #e74c3c;
            box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
            background: rgba(255, 255, 255, 1);
        }
        
        .checkbox-group {
            display: flex;
            gap: 2rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            cursor: pointer;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            background: rgba(236, 240, 241, 0.5);
            border: 2px solid transparent;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        
        .checkbox-item:hover {
            background: rgba(231, 76, 60, 0.05);
            border-color: rgba(231, 76, 60, 0.2);
            transform: translateY(-2px);
        }
        
        .checkbox-item input {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #e74c3c;
        }
        
        .checkbox-item input:checked + span {
            color: #e74c3c;
            font-weight: 600;
        }
        
        .btn-test {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            border: none;
            padding: 1.2rem 3rem;
            font-size: 1.3rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 
                0 8px 25px rgba(231, 76, 60, 0.3),
                0 0 0 1px rgba(231, 76, 60, 0.1);
            font-weight: 700;
            letter-spacing: 0.5px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .btn-test::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn-test:hover::before {
            left: 100%;
        }
        
        .btn-test:hover {
            transform: translateY(-3px);
            box-shadow: 
                0 12px 35px rgba(231, 76, 60, 0.4),
                0 0 0 1px rgba(231, 76, 60, 0.2);
        }
        
        .btn-test:active {
            transform: translateY(-1px);
        }
        
        .btn-test:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 3rem 0;
            padding: 2rem;
            background: rgba(46, 204, 113, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(46, 204, 113, 0.2);
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(46, 204, 113, 0.2);
            border-top: 4px solid #2ecc71;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: #27ae60;
            font-size: 1.3rem;
            font-weight: 600;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        .results {
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.05), rgba(39, 174, 96, 0.05));
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            border: 2px solid rgba(46, 204, 113, 0.2);
            position: relative;
        }
        
        .results::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            border-radius: 15px 15px 0 0;
        }
        
        .results h2 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            font-weight: 700;
        }
        
        .results h2::before {
            content: "✅";
            margin-right: 0.8rem;
            font-size: 1.5rem;
        }
        
        .results pre {
            background: rgba(255, 255, 255, 0.8);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid rgba(46, 204, 113, 0.2);
            overflow-x: auto;
            font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
            line-height: 1.6;
            color: #2c3e50;
            white-space: pre-wrap;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin: 1.5rem 0;
        }
        
        .info-card {
            background: rgba(255, 255, 255, 0.8);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid rgba(52, 73, 94, 0.1);
            text-align: center;
            transition: transform 0.2s ease;
        }
        
        .info-card:hover {
            transform: translateY(-2px);
        }
        
        .info-card strong {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .info-card span {
            display: block;
            color: #e74c3c;
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }
        
        .success-message {
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.1));
            color: #27ae60;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 1.5rem;
            border: 2px solid rgba(46, 204, 113, 0.3);
            font-weight: 600;
        }
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .results-table th, .results-table td {
            padding: 1rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid rgba(236, 240, 241, 0.8);
        }
        
        .results-table th {
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        .results-table tr:hover {
            background: rgba(231, 76, 60, 0.02);
        }
        
        .test-pass {
            color: #27ae60;
            font-weight: 600;
        }
        
        .test-fail {
            color: #e74c3c;
            font-weight: 600;
        }
        
        .icon {
            margin-right: 0.5rem;
        }

        .test-info {
            background: linear-gradient(135deg, rgba(243, 156, 18, 0.05), rgba(230, 126, 34, 0.05));
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border: 2px solid rgba(243, 156, 18, 0.2);
            display: none;
            position: relative;
        }

        .test-info::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #f39c12, #e67e22);
            border-radius: 12px 12px 0 0;
        }

        .test-info h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            font-weight: 700;
            font-size: 1.1rem;
        }

        .test-info h3::before {
            content: "📋";
            margin-right: 0.8rem;
            font-size: 1.2rem;
        }

        .test-info ul {
            padding-left: 2rem;
            color: #34495e;
        }

        .test-info li {
            margin-bottom: 0.8rem;
            line-height: 1.6;
            position: relative;
        }

        .test-info li::before {
            content: "▶";
            position: absolute;
            left: -1.5rem;
            color: #f39c12;
            font-size: 0.8rem;
        }

        .load-test-config {
            display: none;
            margin-top: 1rem;
            padding: 1.5rem;
            background: rgba(41, 128, 185, 0.05);
            border-radius: 12px;
            border: 2px solid rgba(41, 128, 185, 0.2);
            position: relative;
        }

        .load-test-config::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3498db, #2980b9);
            border-radius: 12px 12px 0 0;
        }

        .load-test-config h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            font-weight: 700;
            font-size: 1.1rem;
        }

        .load-test-config h3::before {
            content: "👥";
            margin-right: 0.8rem;
            font-size: 1.2rem;
        }

        @media (max-width: 600px) {
            .container {
                margin: 1rem;
                padding: 2rem;
            }
            
            .header h1 {
                font-size: 2.2rem;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .btn-test {
                padding: 1rem 2rem;
                font-size: 1.1rem;
            }
            
            .checkbox-group {
                flex-direction: column;
                gap: 1rem;
            }

            .checkbox-item {
                min-width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Testeo del Sistema</h1>
            <p>Pruebas automatizadas para Prodovi</p>
        </div>
        
        <form method="POST" class="test-form" id="testForm">
            <div class="form-group">
                <label>Tipo de Prueba:</label>
                <div class="checkbox-group">
                    <label class="checkbox-item">
                        <input type="checkbox" name="test_type" value="smoke" checked>
                        <span>Prueba Smoke</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="test_type" value="load">
                        <span>Prueba de Carga</span>
                    </label>
                    <label class="checkbox-item">
                        <input type="checkbox" name="test_type" value="regression">
                        <span>Prueba Regresion</span>
                    </label>
                </div>

                <div id="smoke-info" class="test-info">
                    <h3>Smoke Test - Pruebas incluidas:</h3>
                    <ul>
                        <li>Carga de página principal</li>
                        <li>Inicio de sesión</li>
                        <li>Acceso al dashboard</li>
                        <li>Creación de planes</li>
                    </ul>
                </div>

                <div id="load-config" class="load-test-config">
                    <h3>Configuración de Prueba de Carga</h3>
                    <div class="form-group">
                        <label for="users">Número de usuarios:</label>
                        <input type="number" id="users" name="users" class="form-control" 
                               min="1" max="1000" value="10" required>
                    </div>
                    <div class="form-group">
                        <label for="spawn_rate">Tasa de usuarios por segundo:</label>
                        <input type="number" id="spawn_rate" name="spawn_rate" class="form-control" 
                               min="1" max="100" value="2" required>
                    </div>
                    <div class="form-group">
                        <label for="run_time">Duración (segundos):</label>
                        <input type="number" id="run_time" name="run_time" class="form-control" 
                               min="1" max="3600" value="30" required>
                    </div>
                </div>

                <div id="regression-info" class="test-info">
                    <h3>Regression Test - Pruebas incluidas:</h3>
                    <ul>
                        <li>Funcionalidad de descarga de archivos de tareas</li>
                        <li>Funcionalidad de descarga de recursos en folders</li>
                    </ul>
                </div>
            </div>
            
            <div class="form-group">
                <label for="email">Correo para enviar reporte:</label>
                <input type="email" id="email" name="email" class="form-control" 
                       placeholder="ejemplo@correo.com" required
                       value="{{ request.form.email if request.form.email else '' }}">
            </div>
            <div class="form-group">
                <label for="mostrar_navegador" style="display: flex; align-items: center; gap: 10px;">
                    <input type="checkbox" id="mostrar_navegador" name="mostrar_navegador" value="true">
                    <span>Mostrar navegador durante las pruebas</span>
                </label>
            </div>
            <button type="submit" class="btn-test" id="testBtn">
                <span class="icon">🚀</span>
                Iniciar Testeo
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div class="loading-text">Ejecutando pruebas... Por favor espere</div>
        </div>
        
        {% if resultado %}
        <div class="results">
            <h2>Resultado del Testeo</h2>
            
            <div class="info-grid">
                <div class="info-card">
                    <strong>Duración</strong>
                    <span>{{ duracion }}s</span>
                </div>
                <div class="info-card">
                    <strong>Fecha y Hora</strong>
                    <span>{{ fecha_hora }}</span>
                </div>
            </div>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Nombre de Prueba</th>
                        <th>Resultado</th>
                        <th>Tiempo de Ejecución</th>
                    </tr>
                </thead>
                <tbody>
                    {% for line in resultado.split('\n') %}
                        {% if line.startswith('V ') or line.startswith('F ') %}
                            {% set test_name = line[2:] %}
                            {% set test_key = line[2:] %}
                        {% elif line.startswith('=== ') %}
                            {% set test_name = line %}
                            {% set test_key = line %}
                            {% set is_header = True %}
                        {% else %}
                            {% set test_name = line %}
                            {% set test_key = line %}
                        {% endif %}

                        <tr>
                            <td>{{ test_name }}</td>
                            <td class="{% if line.startswith('V ') %}test-pass{% elif line.startswith('F ') %}test-fail{% endif %}">
                                {% if line.startswith('V ') %}
                                    ✅ Éxito
                                {% elif line.startswith('F ') %}
                                    ❌ Falló
                                {% elif line.startswith('=== ') %}
                                    ℹ️ Info
                                {% else %}
                                    ℹ️ Info
                                {% endif %}
                            </td>
                            <td>
                                {% if test_key.strip() in tiempos %}
                                    {{ tiempos[test_key.strip()] }}s
                                {% elif line.startswith('=== ') %}
                                    {{ duracion }}s
                                {% else %}
                                    -
                                {% endif %}
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
            <div class="success-message">
                <span class="icon">📧</span>
                <strong>¡Reporte enviado!</strong> Se envió un correo electrónico a <em>{{ request.form.email }}</em> con el reporte detallado.
            </div>
        </div>
        {% endif %}
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const smokeCheckbox = document.querySelector('input[name="test_type"][value="smoke"]');
            const loadCheckbox = document.querySelector('input[name="test_type"][value="load"]');
            const regressionCheckbox = document.querySelector('input[name="test_type"][value="regression"]');
            const smokeInfo = document.getElementById('smoke-info');
            const loadConfig = document.getElementById('load-config');
            const regressionInfo = document.getElementById('regression-info');
            
            function toggleInfo(checkbox, infoDiv) {
                if (checkbox.checked) {
                    infoDiv.style.display = 'block';
                } else {
                    infoDiv.style.display = 'none';
                }
            }
            
            smokeCheckbox.addEventListener('change', function() {
                toggleInfo(smokeCheckbox, smokeInfo);
            });
            
            loadCheckbox.addEventListener('change', function() {
                toggleInfo(loadCheckbox, loadConfig);
            });
            
            regressionCheckbox.addEventListener('change', function() {
                toggleInfo(regressionCheckbox, regressionInfo);
            });
            
            toggleInfo(smokeCheckbox, smokeInfo);
            toggleInfo(loadCheckbox, loadConfig);
            toggleInfo(regressionCheckbox, regressionInfo);
            
            document.getElementById('testForm').addEventListener('submit', function(e) {
                const btn = document.getElementById('testBtn');
                const loading = document.getElementById('loading');
                
                btn.disabled = true;
                btn.innerHTML = '<span class="icon">⏳</span>Testeando...';
                loading.classList.add('show');
                
                loading.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
            
            {% if resultado %}
            const results = document.querySelector('.results');
            if (results) {
                setTimeout(() => {
                    results.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 500);
            }
            {% endif %}
        });
    </script>
</body>
</html>
"""

def run_locust_test(users, spawn_rate, run_time, email_destino):
    """Ejecuta la prueba de carga con Locust y devuelve los resultados"""
    try:
        # Crear archivo de configuración temporal para Locust
        locustfile = os.path.join(os.path.dirname(__file__), 'locustfile.py')
        if not os.path.exists(locustfile):
            raise FileNotFoundError("Archivo locustfile.py no encontrado")
        
        # Comando para ejecutar Locust en modo sin interfaz web
        cmd = [
            'locust',
            '-f', locustfile,
            '--headless',
            '--users', str(users),
            '--spawn-rate', str(spawn_rate),
            '--run-time', f'{run_time}s',
            '--csv=locust_report',
            '--only-summary'
        ]
        
        start_time = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        duration = round(end_time - start_time, 2)
        
        # Leer el reporte generado por Locust
        report = stdout.decode('utf-8')
        if stderr:
            report += "\n\nERRORES:\n" + stderr.decode('utf-8')
        
        # Generar PDF con el reporte
        reporte_path = os.path.join("reportes", f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        generar_pdf(
            texto_resultados=report,
            capturas=[],
            archivo_salida=reporte_path,
            duracion=duration,
            fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tipo_prueba=f"Prueba de Carga ({users} usuarios)"
        )
        
        # Enviar correo con el reporte
        enviar_correo(
            asunto=f"Reporte de Prueba de Carga - {users} usuarios",
            cuerpo=f"Adjunto encontrará el reporte de la prueba de carga realizada.\n\nUsuarios: {users}\nTasa: {spawn_rate} usuarios/seg\nDuración: {run_time} segundos",
            archivo_pdf=reporte_path,
            destino=email_destino
        )
        
        return report, duration
    except Exception as e:
        return f"Error ejecutando prueba de carga: {str(e)}", 0

@app.route("/", methods=["GET", "POST"])
def index():
    resultados_combinados = None
    duracion_total = None
    fecha_hora = None
    pruebas_ejecutadas = []
    tiempos = {}
    mostrar_navegador = request.form.get('mostrar_navegador', 'false') == 'true'

    if request.method == "POST":
        email_destino = request.form.get('email')
        test_types = request.form.getlist('test_type')
        
        all_results = []
        total_duration = 0
        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        capturas = []
        
        if 'smoke' in test_types:
            smoke_result, smoke_duration, _, smoke_tiempos = smoke_test(mostrar_navegador)
            all_results.append("=== Smoke Test Results ===")
            all_results.extend(smoke_result.split('\n'))
            total_duration += smoke_duration
            pruebas_ejecutadas.append("Smoke Test")
            tiempos.update(smoke_tiempos)
            
        if 'load' in test_types:
            users = int(request.form.get('users', 10))
            spawn_rate = int(request.form.get('spawn_rate', 2))
            run_time = int(request.form.get('run_time', 30))
            
            load_result, load_duration = run_locust_test(users, spawn_rate, run_time, email_destino)
            all_results.append(f"\n=== Load Test Results ({users} usuarios) ===")
            all_results.extend(load_result.split('\n'))
            total_duration += load_duration
            pruebas_ejecutadas.append(f"Load Test ({users} usuarios)")
            
        if 'regression' in test_types:
            regression_result, regression_duration, _, regression_tiempos = regression_test(mostrar_navegador)
            all_results.append("\n=== Regression Test Results ===")
            all_results.extend(regression_result.split('\n'))
            total_duration += regression_duration
            pruebas_ejecutadas.append("Regression Test")
            tiempos.update(regression_tiempos)
        
        if all_results:
            resultados_combinados = '\n'.join(all_results)
            duracion_total = round(total_duration, 2)
            fecha_hora = execution_time
            
            tipo_prueba = " + ".join(pruebas_ejecutadas)
            
            # Solo generar PDF si no es una prueba de carga (ya que Locust ya generó su propio reporte)
            if 'load' not in test_types:
                reporte_path = os.path.join("reportes", f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                
                if not os.path.exists("reportes"):
                    os.makedirs("reportes")
                
                generar_pdf(
                    texto_resultados=resultados_combinados,
                    capturas=capturas,
                    archivo_salida=reporte_path,
                    duracion=duracion_total,
                    fecha_hora=fecha_hora,
                    tipo_prueba=tipo_prueba
                )
                
                asunto = f"Reporte de Pruebas Automatizadas - {tipo_prueba}"
                cuerpo = f"Adjunto encontrará el reporte de las pruebas realizadas el {fecha_hora}.\n\nTipo de pruebas: {tipo_prueba}\nDuración total: {duracion_total} segundos"
                
                enviar_correo(
                    asunto=asunto,
                    cuerpo=cuerpo,
                    archivo_pdf=reporte_path,
                    destino=email_destino
                )

    return render_template_string(
        HTML_TEMPLATE, 
        resultado=resultados_combinados, 
        duracion=duracion_total, 
        fecha_hora=fecha_hora,
        tiempos=tiempos
    )

if __name__ == "__main__":
    app.run(debug=True)