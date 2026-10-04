from flask import Flask, render_template, request, jsonify, redirect
from whitenoise import WhiteNoise
import os
# from db.check import check_credentials

import os
from flask import Flask, render_template, request, jsonify, redirect
from whitenoise import WhiteNoise

# --- PURE PYTHON TURSO DRIVER FIX ---
if os.environ.get('RENDER'):
    from libsql_client import create_client_sync
    
    # 1. Fetch your variables securely from Render's dashboard panel
    raw_url = os.environ.get('TURSO_DATABASE_URL', '')
    token = os.environ.get('TURSO_AUTH_TOKEN', '')
    
    # 2. Convert whatever prefix it has (libsql:// or wss://) straight into a stable https:// URL
    clean_url = raw_url.replace("libsql://", "https://").replace("wss://", "https://")
    
    # 3. Bake the authToken query parameter cleanly right into the path string itself
    DB_URI = f"{clean_url}?authToken={token}"
    AUTH_TOKEN = "ACTIVE"  # Acts as a simple internal boolean flag for our if-statement below
else:
    import sqlite3
    DB_URI = 'local_development.db'
    AUTH_TOKEN = None
# -------------------------------------


app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
app.wsgi_app = WhiteNoise(
    app.wsgi_app, 
    root=os.path.join(base_dir, 'static'), 
    prefix='static/'
)

def check_user(username, password):
    if AUTH_TOKEN == "ACTIVE":
        try:
            # Notice we pass ONLY the url string parameter since the token is baked in
            client = create_client_sync(url=DB_URI)
            
            result = client.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?;", 
                [username, password]
            )
            client.close()
            
            return len(result.rows) > 0
            
        except Exception as e:
            print(f"DATABASE ERROR ON RENDER: {e}")
            return False
    else:
        # Local computer fallback
        conn = sqlite3.connect(DB_URI)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?;", (username, password))
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