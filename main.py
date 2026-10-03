from flask import Flask, render_template, request, jsonify, redirect
from whitenoise import WhiteNoise
import os
# from db.check import check_credentials

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
app.wsgi_app = WhiteNoise(
    app.wsgi_app, 
    root=os.path.join(base_dir, 'static'), 
    prefix='static/'
)

default = {
    "username": "admin",
    "password": "admin"
}


def check_user(username, passowrd):
    
    if username == default["username"] and passowrd == default["password"]:
        return True
    else:
        return False

@app.route("/")
def index():
    return render_template("index.html") 

@app.route("/user-home")
def home():
    return render_template("user_home.html")

@app.route("/homepage", methods=["POST"])
def submit_data():
    data_name = request.form['username']
    data_pwd = request.form['pwd']
    
    result = check_user(data_name, data_pwd)

    if result:
        return redirect("/user-home")
    else:
        return "Error, user not found."
    
    
if __name__ == "__main__":
    app.run(debug=True)