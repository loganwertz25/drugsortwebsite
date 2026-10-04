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
    if AUTH_TOKEN:
        try:
            client = create_client_sync(url=DB_URI, auth_token=AUTH_TOKEN)
            
            # Fetch ALL users from your table to see what exists in the cloud
            result = client.execute("SELECT username, password FROM users;")
            client.close()
            
            print(f"--- DATABASE DEBUG LOG ---")
            print(f"Form inputs received -> User: '{username}' | Pass: '{password}'")
            print(f"Total rows found in Turso cloud: {len(result.rows)}")
            
            # Manually loop over the rows to check for an exact match
            for row in result.rows:
                # libsql-client rows behave like lists: index 0 is username, index 1 is password
                db_user = str(row[0]).strip()
                db_pass = str(row[1]).strip()
                
                print(f"Checking against cloud record -> DB User: '{db_user}' | DB Pass: '{db_pass}'")
                
                if db_user == username.strip() and db_pass == password.strip():
                    print("MATCH FOUND! Logging user in...")
                    return True
            
            print("NO MATCH FOUND in the loop.")
            return False
            
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