# 🏏 Cricbuzz LiveStats

> Real-Time Cricket Analytics Dashboard built with Python, Streamlit & SQLite

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-green?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🚀 Live Demo
[👉 Click here to view the app](#)

---

## 📌 About
An interactive multi-page cricket analytics dashboard powered by **22,000+ real match YAML files** from Cricsheet. It stores data in SQLite and provides live dashboards, visualizations, SQL analytics, and full CRUD operations.

---

## ✨ Features
## 📸 Screenshots

### 🏠 Home
![Home](screenshots/home.png)

### 🔍 Search
![Search](screenshots/search.png)

### 📊 Visualizations
![Visualizations](screenshots/visualizations.png)

### 📈 Analytics Overview
![Analytics](screenshots/analytics.png)
| Page | Description |
|------|-------------|
| 🏠 **Home** | KPI cards — Players, Matches, Teams, Venues, Runs, Wickets |
| 🔍 **Search** | Search players, teams, and matches instantly |
| 🔴 **Live Matches** | Live, Recent & Upcoming matches via Cricbuzz API |
| 📊 **Player Stats** | Top run scorers & wicket takers from live API |
| 🧮 **SQL Analytics** | 25 practice SQL queries on real cricket data |
| ⚙️ **CRUD Operations** | Add, update, delete player records |
| 📊 **Visualizations** | Interactive Plotly charts — wins, roles, timelines |
| 📈 **Analytics Overview** | Batting & Bowling leaderboards, Team win tally |
| 🏟️ **Matches CRUD** | Add, update, delete match records |
| 📋 **Scores CRUD** | Add, update, delete player match scores |

---

## 📊 Database Stats
- 🏏 **5,059** Players
- 🏟️ **4,577** Matches
- 🚩 **223** Teams
- 📍 **388** Venues
- 🔥 **1,770,801** Total Runs
- 🎯 **65,846** Total Wickets

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Database:** SQLite
- **Charts:** Plotly Express
- **Data:** Cricsheet YAML (22,000+ files)
- **API:** Cricbuzz via RapidAPI
- **Language:** Python 3.13

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/kilcherushikesh-gif/cricbuzz-livestats.git
cd cricbuzz-livestats/cricbuzz_livestats

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Home.py
```

---
## 👨‍💻 Author ##
**Rushikesh Kilche**
- GitHub: [@kilcherushikesh-gif](https://github.com/kilcherushikesh-gif)

## 📁 Project Structure