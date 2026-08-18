import datetime
import json
import urllib.request
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="AI Calorie Tracker", page_icon="🥗", layout="centered")

# Initialize Session State
if "log_data" not in st.session_state:
    st.session_state.log_data = pd.DataFrame(
        columns=["Date", "Type", "Item", "Calories"]
    )


# Native AI function using raw API (No google-generativeai package needed!)
def estimate_calories_with_ai(food_desc):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        return 200  # Fallback default if key is missing

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = f"Estimate the total calories in: {food_desc}. Reply with ONLY the integer number and nothing else."

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = (
                res_data["candidates"][0]["content"]["parts"][0]["text"]
                .strip()
            )
            # Filter out non-digits just in case
            digits = "".join(filter(str.isdigit, text))
            return int(digits) if digits else 250
    except Exception:
        return 250


st.title("🥗 AI Calorie Tracker & Weight Loss Notebook")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")
tdee = st.sidebar.number_input(
    "Your Daily Maintenance (TDEE) kcal", value=2200, step=50
)

# --- Log Entry Sidebar ---
st.sidebar.header("📝 Smart Log Entry")
food_input = st.sidebar.text_input(
    "What did you eat?", placeholder="e.g., 2 eggs and toast"
)

if st.sidebar.button("Calculate & Add"):
    if food_input.strip() == "":
        st.sidebar.error("Please enter a food description.")
    else:
        with st.spinner("AI is calculating calories..."):
            cals = estimate_calories_with_ai(food_input)
            new_row = pd.DataFrame(
                {
                    "Date": [datetime.date.today()],
                    "Type": ["Food (+)"],
                    "Item": [food_input],
                    "Calories": [cals],
                }
            )
            st.session_state.log_data = pd.concat(
                [st.session_state.log_data, new_row], ignore_index=True
            )
            st.sidebar.success(
                f"Added '{food_input}' (~{cals} kcal) successfully!"
            )

# Manual Exercise Adder
st.sidebar.markdown("---")
st.sidebar.header("🏃 Log Workout")
ex_name = st.sidebar.text_input("Workout Name", placeholder="e.g., Running")
ex_cals = st.sidebar.number_input("Calories Burned", min_value=0, value=150)
if st.sidebar.button("Add Exercise"):
    if ex_name:
        new_row = pd.DataFrame(
            {
                "Date": [datetime.date.today()],
                "Type": ["Exercise (-)"],
                "Item": [ex_name],
                "Calories": [ex_cals],
            }
        )
        st.session_state.log_data = pd.concat(
            [st.session_state.log_data, new_row], ignore_index=True
        )
        st.sidebar.success("Workout logged!")

# --- Main Dashboard ---
if not st.session_state.log_data.empty:
    df = st.session_state.log_data.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    daily_food = df[df["Type"] == "Food (+)"].groupby("Date")["Calories"].sum()
    daily_ex = df[df["Type"] == "Exercise (-)"].groupby("Date")["Calories"].sum()

    summary = pd.DataFrame({"Food": daily_food, "Exercise": daily_ex}).fillna(0)
    summary["Net_Intake"] = summary["Food"] - summary["Exercise"]
    summary["Deficit_Surplus"] = tdee - summary["Net_Intake"]
    summary["Est_Weight_Change_kg"] = summary["Deficit_Surplus"] / 7700

    st.subheader("📊 Your Daily Progress")
    st.dataframe(summary.sort_index(ascending=False), use_container_width=True)

    last_week = summary.tail(7)
    total_est_change = last_week["Est_Weight_Change_kg"].sum()
    st.metric("Estimated Weekly Weight Impact", f"{total_est_change:.2f} kg")
    st.caption(
        "Negative value = Estimated weight loss. Positive value = Estimated weight gain."
    )

    if st.button("Clear All Data"):
        st.session_state.log_data = pd.DataFrame(
            columns=["Date", "Type", "Item", "Calories"]
        )
        st.rerun()
else:
    st.info("Your notebook is empty. Use the sidebar to type what you ate!")
    
