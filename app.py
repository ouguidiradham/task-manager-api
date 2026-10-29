import os
from dotenv import load_dotenv
import sqlite3
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "secretkey")
jwt = JWTManager(app)

conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER, username TEXT)""")
conn.commit()
conn.close()

@app.route("/register", methods=["POST"])
def register():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    data = request.get_json(silent=True)

    if not data :
        return jsonify({"Error": "data not provided"}), 400

    if "username" not in data:
        return jsonify({"Error": "username not provided"}), 400

    if "password" not in data:
        return jsonify({"Error": "password not provided"}), 400

    cursor = conn.cursor()
    hashed = generate_password_hash(data['password'])
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], hashed))
    conn.commit()
    conn.close()

    return jsonify({"Message": f"{data['username']} added successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    data = request.get_json(silent=True)

    if not data :
        return jsonify({"Error": "data not provided"}), 400

    if "username" not in data:
        return jsonify({"Error": "username not provided"}), 400

    if "password" not in data:
        return jsonify({"Error": "password not provided"}), 400

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"Error": "username not found"}), 404

    if not check_password_hash(user[1], data['password']):
        conn.close()
        return jsonify({"Error": "wrong password"}), 401

    token = create_access_token(identity=data['username'])
    conn.close()

    return jsonify({"token": token})

@app.route("/tasks")
@jwt_required()
def get_tasks():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    cursor = conn.cursor()
    username = get_jwt_identity()
    cursor.execute("SELECT * FROM tasks WHERE username = ?", (username,))
    row = cursor.fetchall()
    tasks = [{"id": x[0], "title": x[1], "done": x[2], "username": x[3]} for x in row]
    conn.close()

    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
@jwt_required()
def add_tasks():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    data = request.get_json(silent=True)
    username = get_jwt_identity()

    if not data :
        return jsonify({"Error": "data not provided"}), 400

    if "title" not in data:
        return jsonify({"Error": "title not provided"}), 400

    if "done" not in data:
        return jsonify({"Error": "done not provided"}), 400

    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done, username) VALUES (?, ?, ?)", (data['title'], data['done'], username))
    conn.commit()
    conn.close()

    return jsonify({"Message": " task added successfully"}), 201

@app.route("/tasks/<id>", methods=["DELETE"])
@jwt_required()
def delete_tasks(id):
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    before = len(cursor.fetchall())

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))

    cursor.execute("SELECT * FROM tasks")
    after = len(cursor.fetchall())

    if before == after:
        conn.close()
        return jsonify({"Error": "no id found"}), 404

    conn.commit()
    conn.close()

    return jsonify({"Message": f"{id} deleted successfully"}), 201

@app.route("/tasks/<id>", methods=["PUT"])
@jwt_required()
def update_tasks(id):
    conn = sqlite3.connect("/Users/eaglefly/sqlite/tasks_manager.db")
    data = request.get_json(silent=True)

    if not data :
        return jsonify({"Error": "data not provided"}), 400

    if "done" not in data:
        return jsonify({"Error": "done not provided"}), 400

    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (data['done'], id))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"Error": "id not found"}), 404

    conn.commit()
    conn.close()

    return jsonify({"Message": f"{id} updated successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)