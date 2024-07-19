import streamlit as st
import preprocessor
import pandas as pd
import re
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

# Set page config at the top
st.set_page_config(page_title="ChatViz", layout="wide")

# Sidebar
# Sidebar
st.sidebar.title("📈 **ChatViz**")
st.sidebar.subheader("**WhatsApp Chat Analyzer**")

st.sidebar.markdown(
    """
    **_Analyze and visualize your WhatsApp chat data with insights and graphs_**.

    **Key Features:**
    - 📁 Media Shared
    - 🔗 Links Shared
    - 📅 Monthly & Daily Trends
    - 🌟 Most Active Users
    - ☁️ Word Clouds
    - 😊 Emoji Analysis

    **Upload your chat file** to begin exploring!
    """
)


uploaded_file = st.sidebar.file_uploader("📁 Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis of", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.title("📈 Top Statistics")
        st.write("")

        # Top Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Total Messages")
            st.markdown(f"<h2 style='color: #ff6347;'>{num_messages}</h2>", unsafe_allow_html=True)
        with col2:
            st.subheader("Total Words")
            st.markdown(f"<h2 style='color: #32cd32;'>{num_words}</h2>", unsafe_allow_html=True)
        with col3:
            st.subheader("Media Shared")
            st.markdown(f"<h2 style='color: #1e90ff;'>{num_media}</h2>", unsafe_allow_html=True)
        with col4:
            st.subheader("Links Shared")
            st.markdown(f"<h2 style='color: #ffa500;'>{num_links}</h2>", unsafe_allow_html=True)

        st.write("")
        st.write("")
        
        # Monthly Timeline
        st.title("📅 Monthly Timeline")
        monthly_timeline_df = helper.create_timeline(selected_user, df)

        if not monthly_timeline_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6)) 
            ax.plot(monthly_timeline_df["time"], monthly_timeline_df['message'], linestyle='-', marker='o', color='#8c564b', linewidth=2, markersize=6)
            ax.set_xlabel('Month', fontsize=10)
            ax.set_ylabel('Number of Messages', fontsize=10)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        else:
            st.warning("No data found for the selected user.")

        st.write("")
        st.write("")
        
        # Daily Timeline
        st.title("📅 Daily Timeline")
        daily_timeline_df = helper.daily_timeline(selected_user, df)

        if not daily_timeline_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6)) 
            ax.plot(daily_timeline_df["only_date"], daily_timeline_df['message'], linestyle='-', marker='o', color='#8c564b', linewidth=0.6, markersize=2)
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Number of Messages', fontsize=10)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        else:
            st.warning("No data found for the selected user.")

        st.write("")
        st.write("")

        # Activity Map
        st.title("🗺️ Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color="#d9b3ff", edgecolor="#bf80ff", width=0.6)
            ax.set_xlabel('Day', fontsize=10)
            ax.set_ylabel('Number of Messages', fontsize=10)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="#FFA07A", edgecolor="#FF8C00", width=0.6)
            ax.set_xlabel('Month', fontsize=10)
            ax.set_ylabel('Number of Messages', fontsize=10)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.write("")
        st.write("")

        # Heatmap
        st.title("📊 Weekly Activity Map")
        pivot_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(12,6))
        ax = sns.heatmap(pivot_heatmap)
        st.pyplot(fig)

        st.write("")
        st.write("")

        # Finding busiest users in group
        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = helper.fetch_busy_user(df)
            
            # Convert the index to a list to use as x-axis labels
            user_names = x.index.tolist()
            
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(user_names, x.values, color="#FF6961", edgecolor="r", width=0.6)
                ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
                plt.xticks(rotation="vertical")
                ax.set_xlabel('Users', fontsize=10)
                ax.set_ylabel('Number of Messages', fontsize=10)
                st.pyplot(fig)
            
            with col2:
                st.dataframe(new_df)
        
        st.write("")
        st.write("")

        # Word cloud
        st.title("☁️ Word Cloud")
        df_wc = helper.create_word_cloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots(figsize=(12, 3))
            ax.imshow(df_wc)
            plt.axis('off')
            st.pyplot(fig)
        else:
            st.warning("No words found for the selected user.")

        st.write("")
        st.write("")

        # Most common words
        st.title("📚 Most Common Words")
        new_df = helper.most_common_words(selected_user, df)
        if not new_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6)) 
            ax.barh(new_df['message'], new_df['counts'], color="#FF6961", height=0.8)
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            plt.xticks(rotation="horizontal")
            st.pyplot(fig)
        
        else:
            st.warning("No common words found for the selected user.")
        # st.dataframe(new_df)

        st.write("")
        st.write("")

        # Emoji analysis
        st.title("😊 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if emoji_df is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig = px.pie(emoji_df, values='count', names='emoji', title="Emoji Usage", color_discrete_sequence=px.colors.sequential.RdBu)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(title_font_size=20, title_x=0.5)
                st.plotly_chart(fig)
        else:
            st.warning("No emojis found for the selected user.")
