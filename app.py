import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Weight Loss Daily Notebook", page_icon="🥗", layout="centered"
)

# Initialize Session State for Data Storage
if "log_data" not in st.session_state:
    st.session_state.log_data = pd.DataFrame(
        columns=[
            "Date",
            "Type",
            "Item",
            "Calories",
        ]  # Type: 'Food' or 'Exercise'
    )

st.title("🥗 Weight Loss Daily Notebook")
st.markdown("Track your daily intake, workouts, and stay on top of your goals.")

# --- Sidebar: Log Daily Entry ---
st.sidebar.header("📝 Log Entry")
log_date = st.sidebar.date_input("Date", datetime.date.today())
entry_type = st.sidebar.radio("Category", ["Food (Calories In)", "Exercise (Calories Out)"])
item_name = st.sidebar.text_input(
    "Description", placeholder="e.g., Grilled Chicken Salad or Running"
)
calories = st.sidebar.number_input("Calories", min_value=0, step=10, value=100)

if st.sidebar.button("Add to Notebook"):
    if item_name.strip() == "":
        st.sidebar.error("Please enter a description.")
    else:
        new_row = pd.DataFrame(
            {
                "Date": [pd.to_datetime(log_date)],
                "Type": [entry_type],
                "Item": [item_name],
                "Calories": [int(calories)],
            }
        )
        st.session_state.log_data = pd.concat(
            [st.session_state.log_data, new_row], ignore_index=True
        )
        st.sidebar.success("Logged successfully!")

# --- Main Dashboard ---
tab1, tab2 = st.tabs(["📊 Weekly Report", "📋 Full History"])

with tab1:
    st.header("Weekly Calorie Summary")

    if st.session_state.log_data.empty:
        st.info(
            "Your notebook is empty! Use the sidebar to log your first meal or workout."
        )
    else:
        df = st.session_state.log_data.copy()
        df["Date"] = pd.to_datetime(df["Date"])

        # Separate Food and Exercise
        food_df = df[df["Type"] == "Food (Calories In)"]
        exercise_df = df[df["Type"] == "Exercise (Calories Out)"]

        # Group by Date
        daily_food = (
            food_df.groupby(df["Date"].dt.date)["Calories"].sum().reset_index()
        )
        daily_food.columns = ["Date", "Calories In"]

        daily_exercise = (
            exercise_df.groupby(df["Date"].dt.date)["Calories"].sum().reset_index()
        )
        daily_exercise.columns = ["Date", "Calories Burned"]

        # Merge daily summaries
        summary_df = pd.merge(daily_food, daily_exercise, on="Date", how="outer").fillna(
            0
        )
        summary_df["Net Calories"] = (
            summary_df["Calories In"] - summary_df["Calories Burned"]
        )
        summary_df = summary_df.sort_values(by="Date", ascending=False)

        # Display Metrics for the Latest Day
        if not summary_df.empty:
            latest = summary_df.iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("Latest Calories In", f"{int(latest['Calories In'])} kcal")
            col2.metric(
                "Latest Calories Burned", f"{int(latest['Calories Burned'])} kcal"
            )
            col3.metric("Latest Net Calories", f"{int(latest['Net Calories'])} kcal")

        st.subheader("Daily Breakdown")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Weekly Total / Average
        st.subheader("Weekly Overview (Last 7 Days)")
        last_7_days = summary_df.head(7)
        avg_in = last_7_days["Calories In"].mean()
        avg_out = last_7_days["Calories Burned"].mean()
        avg_net = last_7_days["Net Calories"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Daily Intake", f"{int(avg_in)} kcal")
        col2.metric("Avg Daily Burn", f"{int(avg_out)} kcal")
        col3.metric("Avg Daily Net", f"{int(avg_net)} kcal")

with tab2:
    st.header("All Logged Entries")
    if st.session_state.log_data.empty:
        st.info("No entries logged yet.")
    else:
        display_df = st.session_state.log_data.copy()
        display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.date
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if st.button("Clear All Data"):
            st.session_state.log_data = pd.DataFrame(
                columns=["Date", "Type", "Item", "Calories"]
            )
            st.rerun()
      
