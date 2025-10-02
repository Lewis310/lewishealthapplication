# streamlit_health_report.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime

# ---- Helper functions ----
def load_activity(file):
    df = pd.read_csv(file)
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_nutrition(file):
    df = pd.read_csv(file)
    df['date'] = pd.to_datetime(df['date'])
    return df

def generate_recommendations(row, weight_kg=75, protein_per_kg=1.2):
    recs = []
    protein_target = weight_kg * protein_per_kg
    if row.get("protein_g", None) and row["protein_g"] < protein_target:
        recs.append(f"Protein low ({row['protein_g']}g, target {int(protein_target)}g).")
    if row["active_minutes"] < 20:
        recs.append("Low activity — add a short walk.")
    if row["sleep_minutes"] < 360:
        recs.append("Short sleep — prioritize recovery.")
    if not recs:
        recs.append("Balanced day — keep it up!")
    return "; ".join(recs)

# ---- Streamlit app ----
st.title("Huawei Health Daily & Weekly Report")

activity_file = st.file_uploader("Upload Activity CSV", type=["csv"])
nutrition_file = st.file_uploader("Upload Nutrition CSV (optional)", type=["csv"])

if activity_file:
    act_df = load_activity(activity_file)
    if nutrition_file:
        nut_df = load_nutrition(nutrition_file)
        df = pd.merge(act_df, nut_df, on="date", how="left")
    else:
        df = act_df.copy()

    # Recommendations
    df["recommendation"] = df.apply(generate_recommendations, axis=1)

    # Show daily table
    st.subheader("Daily Data & Recommendations")
    st.dataframe(df)

    # Weekly summary
    st.subheader("Weekly Summary")
    last7 = df.tail(7)
    st.write({
        "Total Calories Burned": last7["calories_burned"].sum(),
        "Avg Sleep (hrs)": round(last7["sleep_minutes"].mean() / 60, 1),
        "Avg Protein (g)": round(last7["protein_g"].mean(), 1) if "protein_g" in last7 else "N/A"
    })

    # Charts
    st.subheader("Charts")
    fig, ax = plt.subplots()
    df.set_index("date")["calories_burned"].plot(ax=ax, marker="o")
    ax.set_title("Calories Burned Over Time")
    st.pyplot(fig)

    # Download report
    st.subheader("Download Report")
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="health_report.csv", mime="text/csv")
