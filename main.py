from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any browser to read your API locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is a 'helper' function that talks to the database
def generate_risk_report():
    connection = sqlite3.connect("firm_records.db")
    cursor = connection.cursor()

    # Query the database like it was in the terminal script
    cursor.execute("SELECT title, risk_score FROM laws ORDER BY risk_score DESC")
    results = cursor.fetchall()
    connection.close()

    # Build a list to hold the formatted data
    dashboard_data = []

    for row in results:
        title = row[0]
        score = row[1]

        if score >= 8:
            status, action = ("CRITICAL", "MANDATORY AUDIT")
        elif score >= 4:
            status, action = ("WARNING", "HUMAN REVIEW")
        else:
            status, action = ("SAFE", "LOGGED")

        # Instead of printing, we append a 'dictionary' to our list
        dashboard_data.append({
            "law_title": title,
            "severity_score": score,
            "system_status": status,
            "required_action": action
        })

    return dashboard_data

@app.get("/api/risk-dashboard")
def risk_dashboard():
    data = generate_risk_report()
    # We return the total count and the data itself
    return {
        "active_alerts": len(data),
        "registry_data": data
    }