from flask import Flask, render_template, request, jsonify, redirect
from whitenoise import WhiteNoise
import os
# from db.check import check_credentials

if os.environ.get('RENDER'):
    from libsql_client import create_client_sync
    
    DB_URI = os.environ.get('libsql://drugsorterdb-loganwertz25.aws-us-west-2.turso.io')
    AUTH_TOKEN = os.environ.get('eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTEwNjk0MTAsImlkIjoiMDFhMTA0MGMtMDcwMS03OTA1LWJiYTktM2YyMzM5NDU1ZDBlIiwia2lkIjoiRXBBZ0pjdzZVSE95NmlNcGVxWnNCSWpQdm1oSmwyc2ZWVXFwbWZtc29PZyIsInJpZCI6ImIwNjdjNDFlLTk5OGEtNDQ1Mi1iNzRkLTYwZjhlODY5ZGVhMiJ9.9lk3kqAPohf18M0Gshg3udJ2xRp4FkdyfqqSk8hCuLUgJrgPBNT3csQ57o09tiQAOZzXHQs62j5pBETgndxNBA')
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
        # Open a secure connection wrapper
        client = create_client_sync(url=DB_URI, auth_token=AUTH_TOKEN)
        
        # Execute query and pull the rows
        result = client.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?;", 
            [username, password]
        )
        client.close()
        
        # If rows list isn't empty, the user exists
        return len(result.rows) > 0
        
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