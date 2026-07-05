"""
This file (plant_functions.py) is the core backend functions for the Plant Care Tracker application.
It handles CSV data persistence, care tracking, and data analysis logic.
"""

import os
import pandas as pd
from datetime import datetime, timedelta

# Define constants for file storage
PLANTS_CSV = "Data/plants_collection.csv"
CARE_LOG_CSV = "Data/care_history.csv"


def initialize_storage():
    """
    Ensures the CSV files exist with the correct headers.
    """
    if not os.path.exists(PLANTS_CSV):
        plants_df = pd.DataFrame(columns=[
            "plant_id", "name", "location", "date_acquired",
            "watering_frequency_days", "sunlight_needs",
            "current_height_cm", "photo_path"
        ])
        plants_df.to_csv(PLANTS_CSV, index=False)

    if not os.path.exists(CARE_LOG_CSV):
        log_df = pd.DataFrame(columns=[
            "timestamp", "plant_id", "activity_type",
            "measurement_cm", "notes"
        ])
        log_df.to_csv(CARE_LOG_CSV, index=False)


def load_data():
    """
    Loads data from CSV files into DataFrames.
    Returns: (plants_df, log_df)
    """
    initialize_storage()
    plants_df = pd.read_csv(PLANTS_CSV)
    log_df = pd.read_csv(CARE_LOG_CSV)

    plants_df["plant_id"] = plants_df["plant_id"].astype(str)
    log_df["plant_id"] = log_df["plant_id"].astype(str)

    return plants_df, log_df


def save_data(plants_df, log_df):
    """
    Saves the updated DataFrames back to CSV.
    """
    plants_df.to_csv(PLANTS_CSV, index=False)
    log_df.to_csv(CARE_LOG_CSV, index=False)


def add_new_plant(name, location, date_acquired, watering_freq, sunlight, height=0.0, photo_path="None"):
    """
    Adds a new plant to the collection.
    """
    plants_df, log_df = load_data()

    plant_id = str(int(datetime.now().timestamp()))

    new_plant = {
        "plant_id": plant_id,
        "name": name,
        "location": location,
        "date_acquired": str(date_acquired),
        "watering_frequency_days": int(watering_freq),
        "sunlight_needs": sunlight,
        "current_height_cm": float(height),
        "photo_path": photo_path
    }

    plants_df = pd.concat([plants_df, pd.DataFrame([new_plant])], ignore_index=True)
    save_data(plants_df, log_df)
    return f"Successfully added {name} to your collection!"


def record_care_activity(plant_id, activity_type, measurement=None, notes=""):
    """
    Logs a care event and optional growth measurement.
    Updates current height if a Growth Tracking measurement is provided.
    """
    plants_df, log_df = load_data()
    current_date = datetime.now().strftime("%Y-%m-%d")

    new_log = {
        "timestamp": current_date,
        "plant_id": str(plant_id),
        "activity_type": activity_type,
        "measurement_cm": float(measurement) if measurement else None,
        "notes": notes
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_log])], ignore_index=True)

    if measurement and activity_type == "Growth Tracking":
        plants_df.loc[plants_df["plant_id"] == str(plant_id), "current_height_cm"] = float(measurement)

    save_data(plants_df, log_df)
    return "Care activity successfully recorded!"


def get_current_season():
    """
    Returns the current season based on calendar month.
    """
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"


def calculate_due_plants():
    """
    Calculates which plants are due/overdue for watering with seasonal adjustments.
    Spring/Summer: standard frequency.
    Autumn: +2 days.
    Winter: frequency doubled.
    """
    plants_df, log_df = load_data()
    if plants_df.empty:
        return pd.DataFrame()

    current_season = get_current_season()
    due_plants = []
    today = datetime.now().date()

    for _, plant in plants_df.iterrows():
        pid = plant["plant_id"]
        base_freq = int(plant["watering_frequency_days"])

        # Seasonal adjustments
        if current_season == "Winter":
            adjusted_freq = base_freq * 2
        elif current_season == "Autumn":
            adjusted_freq = base_freq + 2
        else:
            adjusted_freq = base_freq

        # Find the last watering date
        past_waterings = log_df[(log_df["plant_id"] == pid) & (log_df["activity_type"] == "Watering")]

        if not past_waterings.empty:
            past_waterings_sorted = past_waterings.sort_values(by="timestamp", ascending=False)
            last_watered_str = str(past_waterings_sorted.iloc[0]["timestamp"])
            # Handle date-only format from CSV
            last_watered_date = pd.to_datetime(last_watered_str).date()
        else:
            # Never watered — fall back to date acquired
            last_watered_date = pd.to_datetime(str(plant["date_acquired"])).date()

        days_since_water = (today - last_watered_date).days

        if days_since_water >= adjusted_freq:
            due_plants.append({
                "ID": pid,
                "Plant Name": plant["name"],
                "Location": plant["location"],
                "Last Watered": last_watered_date,
                "Days Overdue": days_since_water - adjusted_freq,
                "Seasonal Schedule (Days)": adjusted_freq
            })

    return pd.DataFrame(due_plants)


def search_plants(search_term):
    """
    Filters the plant collection by name or location.
    """
    plants_df, _ = load_data()
    if plants_df.empty:
        return plants_df

    term = str(search_term).lower()

    filtered_df = plants_df[
        plants_df["name"].str.lower().str.contains(term, na=False) |
        plants_df["location"].str.lower().str.contains(term, na=False)
    ]
    return filtered_df


def get_seasonal_reminders():
    """
    Returns seasonal care tips and the current season name.
    """
    season = get_current_season()
    reminders = []

    if season == "Winter":
        reminders.append("❄️ **Winter Dormancy:** Most plants need less water. Check soil moisture before watering.")
        reminders.append("☀️ **Light Shortage:** Move high-light plants closer to south-facing windows.")
    elif season == "Summer":
        reminders.append("🔥 **Summer Heat:** Evaporation is fast — check soil more often.")
        reminders.append("🛡️ **Leaf Burn Risk:** Shield low-light plants from intense afternoon sun.")
    elif season == "Spring":
        reminders.append("🌱 **Spring Growing Season:** Great time to fertilize or repot!")
    elif season == "Autumn":
        reminders.append("🍂 **Autumn Transition:** Growth is slowing — taper off fertilizer.")

    return reminders, season


def diagnose_symptoms(symptoms_list):
    """
    Rule-based diagnostic: suggests issues based on selected visual symptoms.
    """
    diagnoses = []

    if "Yellow leaves" in symptoms_list and "Mushy stems" in symptoms_list:
        diagnoses.append("⚠️ **Overwatering / Root Rot:** Soil is too wet. Let it dry out and check drainage.")
    if "Crispy brown tips" in symptoms_list or "Drooping leaves" in symptoms_list:
        diagnoses.append("🍂 **Underwatering / Low Humidity:** Water thoroughly or try misting.")
    if "Long, stretchy/skinny stems" in symptoms_list:
        diagnoses.append("💡 **Etiolation:** The plant needs more light. Move it to a brighter spot.")
    if "Webbing or tiny spots on leaves" in symptoms_list:
        diagnoses.append("🪳 **Pest Infestation (Spider Mites):** Isolate the plant and wipe leaves with soapy water or neem oil.")

    if not diagnoses:
        return ["✅ No critical issues detected. Keep monitoring!"]

    return diagnoses