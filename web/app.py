from flask import Flask
import os
from nolocked_api import nolocked_api
from nolocked import nolocked

app = Flask(__name__)
app.config["NLT_DB"] = os.path.join("/home/fry/Code/local/temp/NoLockedThreads-Bot/nlt.db")
app.register_blueprint(nolocked_api, url_prefix='/api')
app.register_blueprint(nolocked, url_prefix='/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)