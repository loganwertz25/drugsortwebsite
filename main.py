from flask import Flask, render_template, request, jsonify, redirect
from whitenoise import WhiteNoise
import os
# from db.check import check_credentials

if os.environ.get('RENDER'):
    from libsql_client import create_client_sync
    
    DB_URI = os.environ.get('TURSO_DATABASE_URL')
    AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN')
else:
    import sqlite3
    DB_URI = 'local_development.db'
    AUTH_TOKEN = None

app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
app.wsgi_app = WhiteNoise(
    app.wsgi_app, 
    root=os.path.join(base_dir, 'static'), 
    prefix='static/'
)

def check_user(username, password):
    # Production cloud database validation via libsql-client
    if AUTH_TOKEN:
        try:
            client = create_client_sync(url=DB_URI, auth_token=AUTH_TOKEN)
            
            # FIX: Use named placeholders (:username and :password) and pass variables as a dict
            result = client.execute(
                "SELECT * FROM users WHERE username = :username AND password = :password;", 
                {"username": username, "password": password}
            )
            client.close()
            
            # If rows list isn't empty, the user exists
            return len(result.rows) > 0
            
        except Exception as e:
            print(f"DATABASE ERROR ON RENDER: {e}")
            return False
        
    # Local fallback for offline computer testing
    else:
        conn = sqlite3.connect(DB_URI)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?;", 
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        return user is not None



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