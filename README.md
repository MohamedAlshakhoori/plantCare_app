# plantCare\_app

plant care app to track houseplants' care schedule and maintenance history





# 🌿 Houseplant Care Tracker \& Diagnostics



An interactive, data-driven Streamlit application designed for plant enthusiasts to track maintenance schedules, document growth metrics, log care history, and diagnose common houseplant ailments.



---



## 📌 Problem Statement & Why It Matters

For plant collectors, managing differing care schedules across multiple species can be overwhelming. Missing a watering window or overwatering during a dormant season often leads to plant stress or loss. 



This application bridges that gap by providing a localized assistant. It automates care tracking using a persistent `.csv` file architecture, adjusts watering frequencies dynamically based on calendar seasons, and utilizes a rule-based diagnostic engine to help users troubleshoot visual plant anomalies before they become critical.



---



## 🚀 Features 



### Core Capabilities 

* **Collection Management:** Add new plants to your digital inventory, capturing key indicators: species name, home location, date acquired, base watering frequency, and sunlight requirements.

* **Activity Logging:** Record specific plant care events—including *Watering, Fertilizing, Repotting, and Pruning*—tagged with automated calendar stamps.

* **Smart Dashboard:** Instantly view a streamlined list of exactly which plants are overdue for attention.

* **Dynamic Search Engine:** Filter through your entire botanical collection instantly by querying either plant names or specific home locations.



### Implemented Stretch Goals (Portfolio Enhancements)

1. **Growth Analytics:** Log your plant heights over time. The application automatically renders linear trend graphs showcasing individual plant growth metrics.

2. **Seasonal Care Adjustments:** Core watering algorithms adapt automatically based on the current calendar month (*Winter dormancy intervals double; Autumn timelines extend; Spring/Summer periods stay baseline*).

3. **Targeted Seasonal Advice:** A contextual sidebar updates on startup to feed specific lighting and temperature advice tailored to the active season.

4. **Photo Path Documentation:** Keep trace of visual development by attaching local image file paths to your inventory profiles.

5. **Rule-Based Symptom Diagnostics:** Select specific structural symptoms (e.g., "Yellow leaves", "Crispy brown tips") to receive automated assessments regarding overwatering, low humidity, legginess, or pests.



---



## 🛠️ Architecture \& Tech Stack



The application is engineered with a strict decoupled structure separating business logic from presentation layout:

* **Frontend:** [Streamlit](https://streamlit.io/) (Interactive web framework)

* **Backend Utilities:** Python 3 core scripting (`plant_functions.py`)

* **Data Layer:** Flat-file `.csv` architecture (`plants_collection.csv` and `care_history.csv`) for persistent local storage using Pandas



---



### File Structure

```text

├── app.py                  # Main Streamlit user interface & navigation 

├── plant_functions.py      # Core data models, calculation engines, and CSV automation

├── plants_collection.csv   # Automatically generated database for plant attributes

├── care_history.csv        # Automatically generated ledger tracking historic actions

└── README.md               # Project documentation and portfolio manual



