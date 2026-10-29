# Task Manager API

A REST API built with Python Flask, SQLite, and JWT authentication. Each user can only see and manage their own tasks.

## Features
- User registration and login
- JWT protected routes
- Per-user task management (users see only their own tasks)

## Routes
- POST /register — create a user
- POST /login — login, returns token
- GET /tasks — get your tasks (protected)
- POST /tasks — add a task (protected)
- PUT /tasks/<id> — update task done status (protected)
- DELETE /tasks/<id> — delete a task (protected)

## How to run
pip install flask flask-jwt-extended python-dotenv
python app.py
