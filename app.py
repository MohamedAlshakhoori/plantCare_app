"""
This file (app.py) is streamlit frontend interface for the Plant Care Tracker app.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plant_functions as pf
import time

# Set up the page config
st.set_page_config(
    page_title="Plant Care Tracker",
    page_icon="🌿",
    layout="wide"
)

# Application Header
st.title("🌿 Houseplant Care Tracker & Diagnostics")
st.markdown("Keep your jungle thriving — tracking schedules and monitoring growth.")


# Load Data & Context
plants_df, log_df = pf.load_data()
seasonal_tips, current_season = pf.get_seasonal_reminders()

# Sidebar: Quick Overview & Seasonal Banner
st.sidebar.header(f"🍂 Current Season: {current_season}")
for tip in seasonal_tips:
    st.sidebar.info(tip)


# Main Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Dashboard & Due Care",
    "➕ Add New Plant",
    "💧 Log Care Activity",
    "🔍 Search & Collection",
    "🩺 Plant Doctor"
])


# TAB 1: Dashboard & due for care plants
with tab1:
    st.header("⏳ Plants Awaiting Attention")
    due_plants = pf.calculate_due_plants()

    if due_plants.empty:
        st.success("All your plants are currently hydrated and happy! 🎉")
    else:
        st.warning(f"You have {len(due_plants)} action items requiring attention:")
        st.dataframe(due_plants, use_container_width=True, hide_index=True)


# TAB 2: Add New Plant
with tab2:
    st.header("🌱 Add a New Companion to Your Collection")

    with st.form("add_plant_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Plant Name / Species (e.g., Monstera, Snake Plant)")
            location = st.text_input("Location in Home (e.g., Living Room Window)")
            date_acquired = st.date_input("Date Acquired", datetime.today())

        with col2:
            watering_freq = st.number_input("Standard Watering Frequency (In Days)", min_value=1, value=7)
            sunlight = st.selectbox("Sunlight Needs", ["Low", "Medium", "High"])
            initial_height = st.number_input("Starting Height (Optional, cm)", min_value=0.0, value=0.0)
            photo_path = st.text_input("Photo Reference Local Filepath (Optional)", value="None")

        submitted = st.form_submit_button("Save Plant to Collection")

        if submitted:
            if name.strip() == "" or location.strip() == "":
                st.error("Please supply at least a plant name and location.")
            else:
                msg = pf.add_new_plant(name, location, date_acquired, watering_freq, sunlight, initial_height, photo_path)
                st.success(msg)
                time.sleep(3) # Fix the problem of not showing the success msg
                st.rerun()


# TAB 3: Log Care Activity
with tab3:
    st.header("🪵 Record an Action or Maintenance")

    if plants_df.empty:
        st.info("Your collection is currently empty. Please add a plant first!")
    else:
        plant_options = {f"{row['name']} ({row['location']})": row['plant_id'] for _, row in plants_df.iterrows()}
        selected_display = st.selectbox("Select the plant you cared for:", list(plant_options.keys()))
        selected_pid = plant_options[selected_display]

        activity = st.selectbox("Activity Type", ["Watering", "Fertilizing", "Repotting", "Pruning", "Growth Tracking"])

        measurement = None
        if activity == "Growth Tracking":
            measurement = st.number_input("Record New Height (cm)", min_value=0.1, step=0.5)

        notes = st.text_area("Observations / Notes (Optional)", placeholder="e.g., Spotted a brand new leaf unfolding today!")

        if st.button("Log Care Event"):
            msg = pf.record_care_activity(selected_pid, activity, measurement, notes)
            st.success(msg)
            time.sleep(3)
            st.rerun()

# TAB 4: Search & Full Collection
with tab4:
    st.header("🌿 Complete Plant Inventory")

    search_term = st.text_input("🔍 Filter by Name or Location", "")

    if search_term:
        display_df = pf.search_plants(search_term)
    else:
        display_df = plants_df.copy()

    if display_df.empty:
        st.write("No matching plants found.")
    else:
        for _, plant in display_df.iterrows():
            pid = plant["plant_id"]

            with st.expander(f"🪴 {plant['name']} — Location: {plant['location']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Date Acquired:** {plant['date_acquired']}")
                    st.write(f"**Watering Interval:** Every {plant['watering_frequency_days']} days")
                    st.write(f"**Sunlight Needs:** {plant['sunlight_needs']}")
                    st.write(f"**Current Height:** {plant['current_height_cm']} cm")
                    if plant['photo_path'] and str(plant['photo_path']) != "None":
                        st.caption(f"📁 Image Path: `{plant['photo_path']}`")

                with col2:
                    st.markdown("**Care History**")
                    plant_history = log_df[log_df["plant_id"] == str(pid)]
                    if plant_history.empty:
                        st.caption("No records yet.")
                    else:
                        st.dataframe(
                            plant_history[["timestamp", "activity_type", "notes"]].sort_values(by="timestamp", ascending=False),
                            hide_index=True,
                            use_container_width=True
                        )

                        # Growth trend chart
                        growth_history = plant_history[plant_history["activity_type"] == "Growth Tracking"].copy()
                        growth_history["measurement_cm"] = pd.to_numeric(growth_history["measurement_cm"], errors="coerce")
                        growth_history = growth_history.dropna(subset=["measurement_cm"])
                        if not growth_history.empty:
                            st.markdown("📈 *Growth Metrics*")
                            st.line_chart(growth_history.set_index("timestamp")["measurement_cm"])


# TAB 5: Plant Doctor
with tab5:
    st.header("🩺 Symptom Diagnostics")
    st.markdown("Select visual symptoms your plant is showing to check for probable issues.")

    selected_symptoms = st.multiselect(
        "What problems are you observing?",
        ["Yellow leaves", "Mushy stems", "Crispy brown tips", "Drooping leaves",
         "Long, stretchy/skinny stems", "Webbing or tiny spots on leaves"]
    )

    if st.button("Run Diagnostic"):
        if not selected_symptoms:
            st.info("Please pick one or more symptoms above.")
        else:
            results = pf.diagnose_symptoms(selected_symptoms)
            st.markdown("### 📋 Findings:")
            for diagnosis in results:
                st.markdown(f"- {diagnosis}")