import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"
load_dotenv(ENV_FILE)

api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

url = f"https://{api_host}/stats/v1/topstats/0"
headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": api_host}
params = {"statsType": "mostRuns"}

response = requests.get(url, headers=headers, params=params, timeout=15)
print("Status:", response.status_code)

data = response.json()
with open("topstats_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Top-level keys:", list(data.keys()))