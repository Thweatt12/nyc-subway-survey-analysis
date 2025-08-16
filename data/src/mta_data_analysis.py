import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sqlalchemy import create_engine, inspect

def load_and_clean_data(filepath):
    subway = pd.read_csv(filepath)
    subway.columns = (
        subway.columns.str.strip().str.lower().str.replace(' ', '_')
    )

    subway.rename(columns={
        'subway_line_used_most_often': 'line_use',
        'use_of_subway_frequency': 'use_of_sub',
        'average_length_subway_ride': 'avg_time_min',
        'primary_use_of_subway': 'use_of_sub',
        'get_to_subway_via': 'way_to_sub',
        'submitted_at': 'date_time',
        'survey_stop_borough': 'borough',
        'survey_stop_location': 'location',
        'is_subway_affordable': 'opinion_price',
        'overall_satisfaction': 'experience',
        'opinion_on_increased_fees': 'opinion_fees'
    }, inplace=True)

    subway.dropna(inplace=True)
    subway.drop_duplicates(inplace=True)

    # split datetime column
    subway[['date', 'time']] = subway['date_time'].str.split(' @ ', expand=True)
    subway['date'] = pd.to_datetime(subway['date'], format="%m/%d/%Y")
    subway['time'] = pd.to_datetime(subway['time'], format="%I:%M %p").dt.time
    subway.drop(columns=['date_time'], inplace=True)

    # helpful features
    subway['month'] = subway['date'].dt.month
    subway['day_name'] = subway['date'].dt.day_name()
    subway['hour'] = subway['time'].apply(lambda t: t.hour)

    # ensure numeric if avg_time_min/experience are strings
    subway['avg_time_min'] = pd.to_numeric(subway['avg_time_min'], errors='coerce')
    subway['experience']   = pd.to_numeric(subway['experience'], errors='coerce')
    subway.dropna(subset=['avg_time_min', 'experience'], inplace=True)

    # map affordability booleans → labels (adjust if your source uses "Yes/No")
    subway['opinion_price'] = subway['opinion_price'].map({
        True: 'Affordable',
        False: 'Too expensive'
    }).fillna(subway['opinion_price'])  # keep original if not boolean

    return subway

# plotting helpers
def ensure_dir(path="screenshots"):
    os.makedirs(path, exist_ok=True)

def plot_ride_time_by_day(df):
    ensure_dir()
    sns.boxplot(x="day_name", y="avg_time_min", data=df,
                order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.title("Average Subway Ride Time by Day")
    plt.xlabel("Day")
    plt.ylabel("Avg Ride Time (min)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("screenshots/ride_time_by_day.png")
    plt.close()

def plot_ride_time_by_hour(df):
    ensure_dir()
    sns.boxplot(x="hour", y="avg_time_min", data=df)
    plt.title("Average Subway Ride Time by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Avg Ride Time (min)")
    plt.tight_layout()
    plt.savefig("screenshots/ride_time_by_hour.png")
    plt.close()

def plot_satisfaction_vs_time(df):
    ensure_dir()
    sns.boxplot(x="experience", y="avg_time_min", data=df)
    plt.title("Satisfaction vs Ride Time")
    plt.xlabel("Satisfaction")
    plt.ylabel("Avg Ride Time (min)")
    plt.tight_layout()
    plt.savefig("screenshots/satisfaction_vs_time.png")
    plt.close()

def plot_satisfaction_vs_price(df):
    ensure_dir()
    # Use countplot for simple save behavior
    sns.countplot(data=df, x='opinion_price', hue='experience')
    plt.title("Satisfaction vs Affordability Opinion")
    plt.tight_layout()
    plt.savefig("screenshots/satisfaction_vs_price.png")
    plt.close()

def main():
    subway = load_and_clean_data("data/raw/Subway.csv")

    engine = create_engine("sqlite:///subway.db")

    try:
        inspector = inspect(engine)
        table_name = "subway_survey"

        if table_name not in inspector.get_table_names():
            # create table first time
            subway.to_sql(table_name, engine, if_exists="replace", index=False)
        else:
            # append or skip depending on your preference
            # subway.to_sql(table_name, engine, if_exists="append", index=False)
            print(f"Table '{table_name}' already exists — skipping write.")

        # plots (run once)
        plot_ride_time_by_day(subway)
        plot_ride_time_by_hour(subway)
        plot_satisfaction_vs_time(subway)
        plot_satisfaction_vs_price(subway)

    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
