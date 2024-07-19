import pandas as pd
import re
from datetime import datetime

def preprocess(data):
    
    pattern = r'^(\d{2}\/\d{2}\/\d{2}),\s(\d{1,2}:\d{2}\s(?:am|pm))\s-\s((?:\+?\d{1,4}\s?\d{5}\s?\d{5}|[\w\s]+)):\s(.+)$'

    messages = []
    message_dates = []
    users = []
    days = []
    month_names = []
    years = []
    hours = []
    minutes = []
 
    matches = re.finditer(pattern, data, re.MULTILINE)

    for match in matches:
        date = match.group(1)
        time = match.group(2)
        user = match.group(3)
        message = match.group(4)
        messages.append(message)
        users.append(user)
        
        # Combine date and time into a single string
        date_time_str = f"{date}, {time}"
        
        # Convert the string to a datetime object
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y, %I:%M %p')
        
        # Extract components
        day = date_time_obj.day
        month_name = date_time_obj.strftime('%B')
        year = date_time_obj.year
        hour = date_time_obj.hour
        minute = date_time_obj.minute
        
        # Append extracted components to corresponding lists
        days.append(day)
        month_names.append(month_name)
        years.append(year)
        hours.append(hour)
        minutes.append(minute)
        
        # Format the datetime object into the desired string format
        formatted_date_time = date_time_obj.strftime('%d-%m-%Y %H:%M')
        message_dates.append(formatted_date_time)

    df = pd.DataFrame({
    'date': message_dates,
    'user': users,
    'message': messages,
    'day': days,
    'month': month_names,
    'year': years,
    'hour': hours,
    'minute': minutes
    })

    return df

