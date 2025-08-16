import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Read and clean the CSV
subway = pd.read_csv("data/raw/Subway.csv")


# Formatted it so it removes spaces and makes all values lowercase
subway.columns = subway.columns.str.strip().str.lower().str.replace(' ', '_')

# Just changed the names of the columns so it’s easier to look at when I use head()
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

# Dropped NA values
subway.dropna(inplace=True)

# Dropped duplicates
subway.drop_duplicates(inplace=True)

# I split up date and time to get graphs later when dates
subway[['date', 'time']] = subway['date_time'].str.split(' @ ', expand=True)

# This is how I formatted the date with month, day, and year
subway['date'] = pd.to_datetime(subway['date'], format="%m/%d/%Y")

# This is how I formatted time with I being hour, colon to separate, M for minutes, and p for am/pm
subway['time'] = pd.to_datetime(subway['time'], format="%I:%M %p").dt.time

# Removed the date_time column since it’s now useless
subway.drop(columns=['date_time'], inplace=True)

# Made a column for the months
subway['month'] = subway['date'].dt.month

# Made a column for the days of the week
subway['day_name'] = subway['date'].dt.day_name()

# Column for the hour extracted from time
subway['hour'] = subway['time'].apply(lambda t: t.hour)

# Didn't drop the important columns I needed — only dropped if they weren’t filled
subway.dropna(subset=['avg_time_min', 'experience'], inplace=True)

# This fixes the issue of true or false for the opinion price 
subway['opinion_price'] = subway['opinion_price'].map({
    True: 'Affordable',
    False: 'Too expensive'
})

# Plot 1: Average subway ride time by day of the week
sns.boxplot(x="day_name", y="avg_time_min", data=subway,
            order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.title("Average Subway Ride Time by Day")
plt.xticks(rotation=45)
plt.show()
# Plot 2: Average subway ride time by hour of day
sns.boxplot(x="hour", y="avg_time_min", data=subway)
plt.title("Average Subway Ride Time by Hour")
plt.xticks(rotation=45)
plt.show()
# Plot 3: Satisfaction levels vs average ride time
sns.boxplot(x="experience", y="avg_time_min", data=subway)
plt.title("Satisfaction vs Ride Time")
plt.xticks(rotation=45)
plt.show()
sns.catplot(x='opinion_price', hue='experience', kind='count', data=subway)

plt.show()
