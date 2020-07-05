from flask import Flask
import os
from nolocked_api import nolocked_api
from nolocked import nolocked

app = Flask(__name__)
app.config["INCIDENTS_DB"] = os.path.join("")
app.register_blueprint(nolocked_api, url_prefix='/api')
app.register_blueprint(nolocked, url_prefix='/')

if __name__ == "__main__":
    app.run(host='0.0.0.0')