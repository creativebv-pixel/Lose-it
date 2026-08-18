import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Weight Loss Tracker", page_icon="⚖️", layout="centered")

# Initialize Session State
if "log_data" not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Date", "Type", "Item", "Calories"])

st.title("⚖️ Weight Loss Tracker")

# --- New: Goal Settings Sidebar ---
st.sidebar.header("⚙️ Your Settings")
tdee = st.sidebar.number_input("Your Estimated Daily Maintenance (TDEE) kcal", value=2200, step=50)

# --- Log Entry Sidebar ---
st.sidebar.header("📝 Log Entry")
log_date = st.sidebar.date_input("Date", datetime.date.today())
entry_type = st.sidebar.radio("Category", ["Food (+)", "Exercise (-)"])
item_name = st.sidebar.text_input("Description")
calories = st.sidebar.number_input("Calories", min_value=0, step=10, value=100)

if st.sidebar.button("Add"):
    new_row = pd.DataFrame({"Date": [log_date], "Type": [entry_type], "Item": [item_name], "Calories": [int(calories)]})
    st.session_state.log_data = pd.concat([st.session_state.log_data, new_row], ignore_index=True)
    st.rerun()

# --- Main Dashboard ---
if not st.session_state.log_data.empty:
    df = st.session_state.log_data.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    
    # Calculate Daily Totals
    daily_food = df[df["Type"] == "Food (+)"].groupby("Date")["Calories"].sum()
    daily_ex = df[df["Type"] == "Exercise (-)"].groupby("Date")["Calories"].sum()
    
    summary = pd.DataFrame({"Food": daily_food, "Exercise": daily_ex}).fillna(0)
    summary["Net_Intake"] = summary["Food"] - summary["Exercise"]
    # Calorie Balance relative to TDEE
    summary["Deficit_Surplus"] = tdee - summary["Net_Intake"]
    
    # Weight Prediction: 1kg fat ≈ 7700 kcal
    summary["Est_Weight_Change_kg"] = summary["Deficit_Surplus"] / 7700

    st.subheader("📊 Your Daily Progress")
    st.dataframe(summary.sort_index(ascending=False), use_container_width=True)

    # Weekly Summary
    last_week = summary.tail(7)
    total_est_change = last_week["Est_Weight_Change_kg"].sum()
    
    st.metric("Estimated Weekly Weight Impact", f"{total_est_change:.2f} kg")
    st.caption("Negative value = Estimated weight loss. Positive value = Estimated weight gain.")
else:
    st.info("Log your first entry to see your progress.")
    
