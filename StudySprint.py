from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "Hi_Simon!"

TASKS_FILE = "tasks.json"


# Reads tasks from the JSON file and returns them as a dictionary
def read_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"tasks": []}
    with open(TASKS_FILE, "r") as file:
        return json.load(file)


# Writes the given data (tasks) to the JSON file
def write_tasks(data):
    with open(TASKS_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Generates and returns the next available task ID
def get_next_id(tasks):
    return max(task["id"] for task in tasks) + 1 if tasks else 1


# Main page route, sorts and displays tasks by stage and deadline in ascending order
@app.route("/")
def index():
    tasks_data = read_tasks().get("tasks", [])
    for task in tasks_data:
        task["deadline_date"] = datetime.strptime(task["deadline"], "%Y-%m-%d")
    stages = {"To Do": [], "Doing": [], "Done": []}
    for task in sorted(tasks_data, key=lambda x: x["deadline_date"]):
        stages[task["stage"]].append(task)
    return render_template("index.html", stages=stages)


# Route to add a new task, redirects to the home page after adding
@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        tasks_data = read_tasks()
        tasks = tasks_data["tasks"]
        new_task = {
            "id": get_next_id(tasks),
            "title": request.form["title"],
            "description": request.form["description"],
            "priority": int(request.form["priority"]),
            "deadline": request.form["deadline"],
            "stage": request.form["stage"],
        }
        tasks.append(new_task)
        write_tasks(tasks_data)
        flash("New task added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add_task.html")


# Route to update a task's stage via drag-and-drop on the home page
@app.route("/update_task_stage/<int:task_id>", methods=["POST"])
def update_task_stage(task_id):
    tasks_data = read_tasks()
    task = next((t for t in tasks_data["tasks"] if t["id"] == task_id), None)
    if task:
        task["stage"] = request.json["stage"]
        write_tasks(tasks_data)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404


# Helper function to get a task by its ID
def get_task_by_id(task_id):
    tasks_data = read_tasks()
    return next((task for task in tasks_data["tasks"] if task["id"] == task_id), None)


# Route for editing a task, includes logic for deletion
@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    tasks_data = read_tasks()
    task = next((task for task in tasks_data["tasks"] if task["id"] == task_id), None)
    if not task:
        return render_template("404.html"), 404
    if request.method == "POST":
        if "delete" in request.form:
            tasks_data["tasks"] = [t for t in tasks_data["tasks"] if t["id"] != task_id]
            write_tasks(tasks_data)
            flash(f"Task {task_id} deleted successfully!", "success")
            return redirect(url_for("index"))
        task["title"] = request.form["title"]
        task["description"] = request.form["description"]
        task["priority"] = int(request.form["priority"])
        task["deadline"] = request.form["deadline"]
        task["stage"] = request.form["stage"]
        write_tasks(tasks_data)
        flash(f"Task {task_id} updated successfully!", "success")
        return redirect(url_for("index"))
    return render_template("task_edit.html", task=task, task_id=task_id)


# Login route, flashes success message and redirects to home page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        flash("Logged in successfully!", "success")
        return redirect(url_for("index"))
    return render_template("login.html")


# Register route, flashes success message and redirects to home page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        flash("Registered successfully!", "success")
        return redirect(url_for("index"))
    return render_template("register.html")


# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Custom 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Main function to run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
