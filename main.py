from flask import Flask, render_template, request, jsonify, redirect, session
from whitenoise import WhiteNoise
import os
from dotenv import load_dotenv
# from db.check import check_credentials

if os.environ.get('RENDER'):
    from libsql_client import create_client_sync
    
    # 1. Pull the raw URL directly from your Render configuration panel
    raw_url = os.environ.get('TURSO_DATABASE_URL', '')
    token = os.environ.get('TURSO_AUTH_TOKEN', '')
    
    # 2. CRUCIAL: Force the protocol to use standard https:// instead of libsql:// or wss://
    clean_url = raw_url.replace("libsql://", "https://").replace("wss://", "https://")
    
    # 3. Assign the variables cleanly to our global names
    DB_URI = clean_url
    AUTH_TOKEN = token
else:
    import sqlite3
    DB_URI = 'local_development.db'
    AUTH_TOKEN = None
# -------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

base_dir = os.path.dirname(os.path.abspath(__file__))
app.wsgi_app = WhiteNoise(
    app.wsgi_app, 
    root=os.path.join(base_dir, 'static'), 
    prefix='static/'
)

def check_user(username, password):
    # Production cloud database validation via libsql-client over HTTPS
    if AUTH_TOKEN and AUTH_TOKEN != "ACTIVE":
        try:
            # Pass the URL and Token as separate keyword properties
            client = create_client_sync(url=DB_URI, auth_token=AUTH_TOKEN)
            
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
    if not session.get('logged_in'):
        return redirect("/")
    
    return render_template("user_home.html")

@app.route("/homepage", methods=["POST"])
def submit_data():
    data_name = request.form['username']
    data_pwd = request.form['pwd']
    
    result = check_user(data_name, data_pwd)

    if result:
        session['logged_in'] = True
        session['username'] = data_name 
        return redirect("/user-home")
    else:
        return "Error, user not found."
    
@app.route("/logout")
def logout():
    session.clear() # Deletes the login session data
    return redirect("/")
    
    
if __name__ == "__main__":
    app.run(debug=True)