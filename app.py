from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
mongo = PyMongo(app)
CORS(app)

# Google Calendar API Configuration
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_service_account_key.json"
creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json")
if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "path_to_credentials.json", ["https://www.googleapis.com/auth/calendar"]
    )
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())
service = build("calendar", "v3", credentials=creds)


@app.route("/projects", methods=["GET"])
def get_all_projects():
    projects = mongo.db.projects.find()
    response = []
    for project in projects:
        response.append(
            {
                "id": str(project["_id"]),
                "name": project["name"],
                "description": project["description"],
            }
        )
    return jsonify(response)


@app.route("/projects", methods=["POST"])
def create_project():
    name = request.json.get("name")
    description = request.json.get("description")

    project_id = mongo.db.projects.insert({"name": name, "description": description})

    project = mongo.db.projects.find_one({"_id": project_id})

    return jsonify(
        {
            "id": str(project["_id"]),
            "name": project["name"],
            "description": project["description"],
        }
    )


@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = mongo.db.tasks.find()
    response = []
    for task in tasks:
        response.append(
            {
                "id": str(task["_id"]),
                "title": task["title"],
                "description": task["description"],
                "dueDate": task["dueDate"].strftime("%Y-%m-%d"),
                "assignedTo": task["assignedTo"],
            }
        )
    return jsonify(response)


@app.route("/tasks", methods=["POST"])
def create_task():
    title = request.json.get("title")
    description = request.json.get("description")
    due_date_str = request.json.get("dueDate")
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    assigned_to = request.json.get("assignedTo")

    task_id = mongo.db.tasks.insert(
        {
            "title": title,
            "description": description,
            "dueDate": due_date,
            "assignedTo": assigned_to,
        }
    )

    task = mongo.db.tasks.find_one({"_id": task_id})

    return jsonify(
        {
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task["description"],
            "dueDate": task["dueDate"].strftime("%Y-%m-%d"),
            "assignedTo": task["assignedTo"],
        }
    )


@app.route("/calendar-events", methods=["GET"])
def get_calendar_events():
    try:
        events_result = (
            service.events()
            .list(calendarId="primary", timeMin=datetime.utcnow().isoformat() + "Z")
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "No events found."
        response = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            response.append(
                {
                    "title": event["summary"],
                    "start": start,
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                }
            )
        return jsonify(response)
    except HttpError as error:
        print("An error occurred: %s" % error)
        return "Error"


@app.route("/search", methods=["GET"])
def search_tasks():
    query = request.args.get("query")
    tasks = mongo.db.tasks.find({"$text": {"$search": query}})

    response = []
    for task in tasks:
        response.append(
            {
                "id": str(task["_id"]),
                "title": task["title"],
                "description": task["description"],
                "dueDate": task["dueDate"].strftime("%Y-%m-%d"),
                "assignedTo": task["assignedTo"],
            }
        )

    return jsonify(response)


if __name__ == "main":
    app.run()
