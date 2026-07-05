"""
This file (plant_functions.py) contains the
core backend functions for the Plant Care Tracker application.
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
    Loads empty DataFrames if files are missing.
    """
    # Base plant details schema
    if not os.path.exists(PLANTS_CSV):
        plants_df = pd.DataFrame(columns=[
            "plant_id", "name", "location", "date_acquired", 
            "watering_frequency_days", "sunlight_needs", 
            "current_height_cm", "photo_path"
        ])
        plants_df.to_csv(PLANTS_CSV, index=False)
        
    # Care history log schema (tracks historical actions + growth)
    if not os.path.exists(CARE_LOG_CSV):
        log_df = pd.DataFrame(columns=[
            "timestamp", "plant_id", "activity_type", 
            "measurement_cm", "notes"
        ])
        log_df.to_csv(CARE_LOG_CSV, index=False)


def load_data():
    """
    Loads data from the CSV files into Pandas DataFrames.
    Returns: (plants_df, log_df)
    """
    initialize_storage()
    plants_df = pd.read_csv(PLANTS_CSV)
    log_df = pd.read_csv(CARE_LOG_CSV)
    
    # Ensure plant_id is treated consistently (as strings or integers)
    plants_df["plant_id"] = plants_df["plant_id"].astype(str)
    log_df["plant_id"] = log_df["plant_id"].astype(str)
    
    return plants_df, log_df


def save_data(plants_df, log_df):
    """
    Saves the updated DataFrames back into the CSV files.
    """
    plants_df.to_csv(PLANTS_CSV, index=False)
    log_df.to_csv(CARE_LOG_CSV, index=False)


def add_new_plant(name, location, date_acquired, watering_freq, sunlight, height=0.0, photo_path="None"):
    """
    Adds a new plant to the collection and updates the CSV.
    """
    plants_df, log_df = load_data()
    
    # Generate a unique plant ID based on current timestamp
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
    Logs a care event (Watering, Repotting, etc.) and optional growth metrics to the history log. 
    It updates current height if provided.
    """
    plants_df, log_df = load_data()
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Log the action
    new_log = {
        "timestamp": current_date,
        "plant_id": str(plant_id),
        "activity_type": activity_type,
        "measurement_cm": float(measurement) if measurement else "",
        "notes": notes
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_log])], ignore_index=True)
    
    # If a growth measurement was recorded, update the primary plant index
    if measurement and activity_type == "Growth Tracking":
        plants_df.loc[plants_df["plant_id"] == str(plant_id), "current_height_cm"] = float(measurement)
        
    save_data(plants_df, log_df)
    return "Care activity successfully recorded!"


def get_current_season():
    """
    Helper function to determine the current season based on calendar month.
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
    Calculates which plants are due for watering,
    dynamically adjusting schedules based on the current season.
    
    * Spring/Summer: Standard frequency.
    * Autumn: Adds 2 days to the frequency.
    * Winter: Doubles the watering interval (plants go dormant).
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
        
        # Stretch Goal 4: Seasonal adjustments logic
        if current_season == "Winter":
            adjusted_freq = base_freq * 2
        elif current_season == "Autumn":
            adjusted_freq = base_freq + 2
        else:
            adjusted_freq = base_freq  # Spring/Summer standard growth
            
        # Find the last watering date from care history
        past_waterings = log_df[(log_df["plant_id"] == pid) & (log_df["activity_type"] == "Watering")]
        
        if not past_waterings.empty:
            # Sort logs and grab the most recent timestamp
            past_waterings_sorted = past_waterings.sort_values(by="timestamp", ascending=False)
            last_watered_str = past_waterings_sorted.iloc[0]["timestamp"]
            last_watered_date = datetime.strptime(last_watered_str, "%Y-%m-%d").date()
        else:
            # If never watered, fall back to the date it was acquired
            last_watered_date = datetime.strptime(plant["date_acquired"], "%Y-%m-%d").date()
            
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
    Filter plants database by name or location.
    """
    plants_df, _ = load_data()
    if plants_df.empty:
        return plants_df
        
    term = str(search_term).lower()
    filtered_df = plants_df[
        plants_df["name"].str.lower().str.contains(term) | 
        plants_df["location"].str.lower().str.contains(term)
    ]
    return filtered_df


def get_seasonal_reminders():
    """
    Generates customized tips based on the current season and the plant's sunlight needs.
    """
    season = get_current_season()
    reminders = []
    
    if season == "Winter":
        reminders.append("❄️ **Winter Dormancy Active:** Most plants need significantly less water right now. Check soil moisture first.")
        reminders.append("☀️ **Light Shortage:** Move 'High' sunlight plants closer to south-facing windows to maximize sunlight.")
    elif season == "Summer":
        reminders.append("🔥 **Summer Heat Spike:** Evaporation happens fast. Check soil levels twice as often.")
        reminders.append("🛡️ **Leaf Burn Risk:** Guard 'Low' light plants against intense, direct afternoon sun.")
    elif season == "Spring":
        reminders.append("🌱 **Spring Growing Season:** Perfect time to start your **Fertilizing** or **Repotting** activities!")
    elif season == "Autumn":
        reminders.append("🍂 **Autumn Transition:** Growth is slowing down. Begin tapering off fertilizer.")
        
    return reminders, season


def diagnose_symptoms(symptoms_list):
    """
    Rule-based diagnostic tool to suggest issues based on selected symptoms.
    """
    diagnoses = []
    
    if "Yellow leaves" in symptoms_list and "Mushy stems" in symptoms_list:
        diagnoses.append("⚠️ **Overwatering / Root Rot:** The soil is likely holding too much moisture. Let it dry completely and check drainage holes.")
    if "Crispy brown tips" in symptoms_list or "Drooping leaves" in symptoms_list:
        diagnoses.append("🍂 **Underwatering / Low Humidity:** The plant is thirsty or the air is too dry. Consider a thorough watering soak or misting.")
    if "Long, stretchy/skinny stems" in symptoms_list:
        diagnoses.append("💡 **Legginess (Etoliation):** The plant is searching for light. Move it to a spot with a higher sunlight rating.")
    if "Webbing or tiny spots on leaves" in symptoms_list:
        diagnoses.append("🪳 **Pest Infestation (e.g., Spider Mites):** Isolate the plant immediately and wipe leaves down with soapy water or neem oil.")
        
    if not diagnoses:
        return ["✅ No critical problems detected based on selected symptoms. Keep monitoring your plant!"]
        
    return diagnoses