from flask import Flask,render_template
from backend.models import *
app = None

def init_app():
    iescp = Flask(__name__)
    iescp.debug = True
    iescp.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///iescp.sqlite3"
    iescp.app_context().push()
    db.init_app(iescp)
    print("Server started")
    return iescp
app = init_app()

from backend.controllers import *

if __name__ =="__main__":
    app.run()