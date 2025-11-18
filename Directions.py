from flask import Flask, request
from flask_cors import CORS

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage 
# Blueprints
from BackEnd.Directions.authDirections import authBluePrint
from BackEnd.Directions.serviceDirections import serviceBluePrint

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Acepta rutas con y sin slash final
app.url_map.strict_slashes = False

# CORS
CORS(app)

# Registra blueprints
app.register_blueprint(authBluePrint)
app.register_blueprint(serviceBluePrint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6002, debug=True, threaded=True)
