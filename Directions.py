from flask import Flask, request
from flask_cors import CORS
import os

# Blueprints
from BackEnd.Directions.authDirections import authBluePrint
from BackEnd.Directions.serviceDirections import serviceBluePrint
from BackEnd.Directions.projectDirections import projectBluePrint
from BackEnd.Directions.IteracionesDirections import IteracionesBluePrint
from BackEnd.Directions.planDirections import planBluePrint
from BackEnd.Directions.artifactDirections import artifactBluePrint
from BackEnd.Directions.permissionsDirections import permissionsBluePrint
from BackEnd.Directions.microDirections import microBluePrint
from BackEnd.Directions.progressDirections import progressBluePrint
from BackEnd.Directions.workflowDirections import workflowBluePrint
from BackEnd.Directions.testDirections import testBluePrint
from BackEnd.Directions.defectDirections import defectBluePrint
from BackEnd.Directions.configurationDirections import configurationDirections
from BackEnd.Directions.buildDirections import buildBlueprint
from BackEnd.Directions.exportImportDirections import exportImportBlueprint
from BackEnd.Directions.auditDirections import auditBluePrint
from BackEnd.Directions.projectMembersDirections import projectMembersBluePrint
from BackEnd.Directions.projectClosureDirections import projectClosureBluePrint

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Configuración de sesiones
app.secret_key = os.environ.get('SECRET_KEY', 'openup-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Cambiar a False para desarrollo
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Lax funciona mejor que None sin HTTPS
app.config['SESSION_COOKIE_DOMAIN'] = None  # Permitir localhost
app.config['SESSION_COOKIE_NAME'] = 'openup_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# Acepta rutas con y sin slash final
app.url_map.strict_slashes = False

# CORS con soporte para credenciales
CORS(app, supports_credentials=True, origins=['http://localhost:4200'])

# Allow registering routes after first request (tests sometimes register routes dynamically)
def _no_check(f_name):
    return None
app._check_setup_finished = _no_check

# Registra blueprints
app.register_blueprint(authBluePrint)
app.register_blueprint(serviceBluePrint)
app.register_blueprint(projectBluePrint)
app.register_blueprint(IteracionesBluePrint)
app.register_blueprint(planBluePrint)
app.register_blueprint(artifactBluePrint)
app.register_blueprint(permissionsBluePrint)
app.register_blueprint(microBluePrint)
app.register_blueprint(progressBluePrint)
app.register_blueprint(workflowBluePrint)
app.register_blueprint(testBluePrint)
app.register_blueprint(defectBluePrint)
app.register_blueprint(configurationDirections)
app.register_blueprint(buildBlueprint)
app.register_blueprint(exportImportBlueprint)
app.register_blueprint(auditBluePrint)
app.register_blueprint(projectMembersBluePrint)
app.register_blueprint(projectClosureBluePrint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6002, debug=True, threaded=True)
