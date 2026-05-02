from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import logging
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

my_secret = os.getenv("SECRET_COMPLIANCE_KEY")
print(f"My secure key is loaded: {my_secret}")

# This creates a filed called 'system_audit.log' and records everything at the INFO level or higher.
logging.basicConfig(
    filename='system_audit_log',
    level=logging.INFO,
    format='%(acstime)s - %(levelname)s - %(message)s'
)

# 2 Inside your API:
def evaluate_risk(law_title, severity_score):
    logging.info(f"New case received: Evaluating compliance for {law_title}")

    if severity_score >= 8:
        # This writes permanently to your log file, not just the screen
        logging.critical(f"VIOLATION DETECTED: {law_title} scored {severity_score}/10.")
        return "MANDATORY AUDIT"
    else:
        logging.info("System falls within acceptable legal parameters.")
        return "SAFE"
    

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
