from flask import Flask, request
from flask_cors import CORS

# Blueprints
from BackEnd.Directions.authDirections import authBluePrint
from BackEnd.Directions.serviceDirections import serviceBluePrint
from BackEnd.Directions.projectDirections import projectBluePrint
from BackEnd.Directions.IteracionesDirections import IteracionesBluePrint
from BackEnd.Directions.planDirections import planBluePrint
from BackEnd.Directions.artifactDirections import artifactBluePrint
from BackEnd.Directions.microDirections import microBluePrint
from BackEnd.Directions.progressDirections import progressBluePrint
from BackEnd.Directions.workflowDirections import workflowBluePrint

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Acepta rutas con y sin slash final
app.url_map.strict_slashes = False

# CORS
CORS(app)

# Registra blueprints
app.register_blueprint(authBluePrint)
app.register_blueprint(serviceBluePrint)
app.register_blueprint(projectBluePrint)
app.register_blueprint(IteracionesBluePrint)
app.register_blueprint(planBluePrint)
app.register_blueprint(artifactBluePrint)
app.register_blueprint(microBluePrint)
app.register_blueprint(progressBluePrint)
app.register_blueprint(workflowBluePrint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6002, debug=True, threaded=True)
