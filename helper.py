import pandas as pd
import streamlit as st
from urlextract import URLExtract
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from collections import Counter
import emoji

stop_words = set(stopwords.words('english'))

def fetch_stats(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # no.of messages
    num_messages = df.shape[0]

    # no. of words
    num_words = [] 
    for msg in df['message']:
            num_words.extend(msg.split())

    # no.of media
    num_media = df[df['message'] == "<Media omitted>"].shape[0]

    # no.of links
    extractor = URLExtract()
    num_links = []
    for message in df['message']:
        num_links.extend(extractor.find_urls(message))

    return num_messages, len(num_words), num_media, len(num_links)


def fetch_busy_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'percent':'user', 'count':'percent'}) 
    
    return x, df


def create_word_cloud(selected_user, df):
    
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    df = df[df['message'] != "<Media omitted>"]

    if df.empty or df['message'].isnull().all():
        return None 

    wc = WordCloud(width=500, height=500, min_font_size=18, background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=""))

    return df_wc


def most_common_words(selected_user, df):
    
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp_df = df[df['message'] != "<Media omitted>"]
    words_list = []
    for message in temp_df['message']:
        words = message.lower().split()
        filtered_words = [word for word in words if word not in stop_words]
        words_list.extend(filtered_words)
    
    words_to_remove = ['message', 'deleted', '-', '&']
    words_list = [word for word in words_list if word not in words_to_remove]
    
    word_counts = Counter(words_list).most_common(15)    
    new_df = pd.DataFrame(word_counts, columns=['message', 'counts'])

    if not new_df.empty:
        new_df = new_df.drop(new_df.index[0])

    return new_df


def emoji_helper(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    def is_emoji(character):
        return character in emoji.EMOJI_DATA
    
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if is_emoji(c)])
    
    if not emojis:
        return None
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ['emoji', 'count']

    return emoji_df



def create_timeline(selected_user, df):
    
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    df['month_date'] = pd.to_datetime(df['date'], format="%d-%m-%Y %H:%M")
    df['month_num'] = df['month_date'].dt.month
    df['year'] = df['month_date'].dt.year
    df['month'] = df['month_date'].dt.strftime('%B')  # Full month name

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    
    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    df['month_date'] = pd.to_datetime(df['date'], format="%d-%m-%Y %H:%M")
    
    df['only_date'] = df['month_date'].dt.date
    daily_timeline = df.groupby(df['only_date']).count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    df['month_date'] = pd.to_datetime(df['date'], format="%d-%m-%Y %H:%M")
    df['day_name'] = df['month_date'].dt.day_name()

    return df['day_name'].value_counts()



def month_activity_map(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    
    df['month_date'] = pd.to_datetime(df['date'], format="%d-%m-%Y %H:%M")
    df['day_name'] = df['month_date'].dt.day_name()

    period = []
    for hour in df[['day_name','hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') +"-" + str(hour+1))
        else:
            period.append(str(hour) + "-" + str(hour+1)) 
        
    df['period'] = period

    pivot_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return pivot_heatmap
    



