from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji


extract = URLExtract()

def fetch_stats(selected_user, df):

    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]

    num_messages = temp.shape[0]

    words = []
    for msg in temp['message']:
        words.extend(msg.split())

    num_media = temp[temp['message'].str.contains("Media omitted")].shape[0]

    links = []
    for msg in temp['message']:
        links.extend(extract.find_urls(msg))

    return num_messages, len(words), num_media, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df2 = round((df['user'].value_counts() / df.shape[0]) * 100, 2)\
        .reset_index().rename(columns={'user': 'Name', 'count': 'Percent'})
    return x, df2


def create_wordcloud(selected_user, df):
    with open("stop_hinglish.txt", "r") as f:
        stop_words = set(f.read().split())

    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    temp = temp[temp['user'] != "Group Notification aaya hai harsh"]
    temp = temp[~temp['message'].str.contains("Media omitted")]

    def clean(msg):
        return " ".join([w for w in msg.lower().split() if w not in stop_words])

    temp['clean'] = temp['message'].apply(clean)

    wc = WordCloud(width=600, height=400, background_color="white")
    return wc.generate(" ".join(temp['clean'].tolist()))


def most_common_words(selected_user, df):
    with open("stop_hinglish.txt", "r") as f:
        stop_words = set(f.read().split())

    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    temp = temp[temp['user'] != "Group Notification aaya hai harsh"]
    temp = temp[~temp['message'].str.contains("Media omitted")]

    words = []
    for msg in temp['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(30))


def emoji_helper(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]

    emojis = []
    for msg in temp['message']:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common())


def monthly_timeline(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    t = temp.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    t['time'] = t['month'] + "-" + t['year'].astype(str)
    return t


def daily_timeline(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    return temp.groupby('only_date').count()['message'].reset_index()


def week_activity_map(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    return temp['day_name'].value_counts()


def monthly_activity_map(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    return temp['month'].value_counts()


def activity_heatmap(selected_user, df):
    temp = df if selected_user == "Overall" else df[df['user'] == selected_user]
    return temp.pivot_table(index='day_name', columns='period',
                            values='message', aggfunc='count', fill_value=0)
