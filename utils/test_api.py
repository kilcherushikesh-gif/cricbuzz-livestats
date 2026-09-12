import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST")

print("API key found:", bool(api_key))
print("API key value (first 6 chars):", api_key[:6] if api_key else None)

if not api_key:
    raise SystemExit("No API key loaded — check your .env file location and variable name.")

url = f"https://{api_host}/matches/v1/recent"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": api_host
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response:", response.text[:500])