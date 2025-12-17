

import streamlit as st
st.markdown("""
###  How to Use This Tool

1️⃣ **WhatsApp → Export Chat**
- Open any chat → Tap 3 dots → More → Export Chat
- Select Without Media
- A ZIP file will be downloaded

2️⃣ Extract the ZIP
- Inside it, you’ll find a **.txt** chat file

3️⃣ **Upload the .txt file here**
- Click **Browse files** and select your chat file

4️⃣ **Choose User or Overall**
- Select a specific person or analyze the entire chat

5️⃣ **Click “Show Analysis”**
- View messages stats, wordcloud, emoji analysis & more 🚀

""")
import preprocessor, helper
import re
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")
    df=preprocessor.preprocess(data)

    #fetch unique users
    user_list=df['user'].unique().tolist()
    if 'Group Notification aaya hai harsh' in user_list:
        user_list.remove('Group Notification aaya hai harsh')

    user_list.sort(key=str.lower)
    user_list.insert(0,'Overall')

    selected_user=st.sidebar.selectbox("Choose a user",user_list)

    if st.sidebar.button('Show Analysis'):

        num_messages, words, num_media_messages, links=helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1,col2,col3,col4 = st.columns(4)

        with col1:
            st.header('Total Messages')
            st.title(num_messages)

        with col2:
            st.header('Total words')
            st.title(words)

        with col3:
            st.header('Media Shared')
            st.title(num_media_messages)

        with col4:
            st.header('Links')
            st.title(links)

        #Monthly Timeline
        st.title("Monthly Timeline")
        timeline=helper.monthly_timeline(selected_user,df)
        fig,ax=plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        #Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        plt.figure(figsize=(18,10))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='green')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        #activity map
        st.title('Activity Map')
        col1,col2=st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day=helper.week_activity_map(selected_user,df)
            fig,ax=plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month=helper.monthly_activity_map(selected_user,df)
            fig,ax=plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='pink')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap=helper.activity_heatmap(selected_user,df)
        fig, ax = plt.subplots()
        ax=sns.heatmap(user_heatmap)
        st.pyplot(fig)





