# import re
# import pandas as pd
#
# def preprocess(data):
#     pattern = r'\d{2}\/\d{2}\/\d{2},\s+\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\s+-'
#     # pattern = r"^(\d{1,2}\/\d{1,2}\/\d{2,4}), (\d{1,2}:\d{2}(?:\s?[ap]m)?) - (.*?): (.*)"
#
#     messages = re.split(pattern, data)[1:]
#
#     dates = re.findall(pattern, data)
#
#     df = pd.DataFrame({
#         'user_message': messages,
#         'message_date': dates
#     })
#
#     # Fix Unicode narrow space issue
#     df['message_date'] = df['message_date'].astype(str).str.replace('\u202f', ' ', regex=False)
#
#     # Convert to datetime
#     df['message_date'] = pd.to_datetime(
#         df['message_date'],
#         format='%d/%m/%y, %I:%M %p -'
#     )
#
#     # Rename
#     df.rename(columns={'message_date': 'date'}, inplace=True)
#
#     # username aur messages ko separate kro
#     df = pd.DataFrame({'user_message': messages, 'message_date': dates})
#
#     users = []
#     msgs = []
#
#     for m in df['user_message']:
#         parts = re.split(r'^(.*?):\s', m, maxsplit=1)
#
#         if len(parts) == 3:
#             users.append(parts[1])
#             msgs.append(parts[2])
#         else:
#             users.append("Group Notification aaya hai harsh")
#             msgs.append(m)
#
#     df['user'] = users
#     df['message'] = msgs
#     df.drop(columns=['user_message'], inplace=True)
#
#     # Fix special WhatsApp space (U+202F)
#     df['date'] = [d.replace('\u202f', ' ') for d in dates]
#
#     # Convert to datetime
#     df['date'] = pd.to_datetime(
#         df['date'],
#         format='%d/%m/%y, %I:%M %p -',
#         errors='coerce'
#     )
#
#     # Extract year, month, day
#     df['year'] = df['date'].dt.year
#     df['month_num']=df['date'].dt.month
#     df['only_date']=df['date'].dt.date
#     df['month'] = df['date'].dt.month_name()
#     df['day'] = df['date'].dt.day
#     df['day_name']=df['date'].dt.day_name()
#     df['hour'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute
#     df['weekday'] = df['date'].dt.day_name()
#
#     period=[]
#     for hour in df[['day_name', 'hour']]['hour']:
#         if hour==23:
#             period.append(str(hour)+"-"+str("00"))
#         elif hour==0:
#             period.append(str("00")+"-"+str(hour+1))
#         else:
#             period.append(str(hour)+"-"+str(hour+1))
#
#     df['period']=period
#
#     return df
#
#

import re
import pandas as pd


# UNIVERSAL DATETIME PARSER
def smart_datetime_parser(date_str):
    if date_str is None:
        return None

    # Fix unicode spaces
    date_str = date_str.replace("\u202f", " ").replace("\u202F", " ")

    formats = [
        "%d/%m/%y, %I:%M %p -",
        "%d/%m/%Y, %I:%M %p -",
        "%d/%m/%y, %H:%M -",
        "%d/%m/%Y, %H:%M -",
        "%m/%d/%y, %I:%M %p -",
        "%m/%d/%Y, %I:%M %p -",
        "%m/%d/%y, %H:%M -",
        "%m/%d/%Y, %H:%M -",
    ]

    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue

    return None


def preprocess(data):

    # Universal WhatsApp regex
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?: ?[APMapm]{2})? - )"

    parts = re.split(pattern, data)

    dates = []
    messages = []

    for i in range(1, len(parts), 2):
        dates.append(parts[i])
        messages.append(parts[i + 1])

    df = pd.DataFrame({'raw_date': dates, 'user_message': messages})

    # When regex fails completely → empty DF
    if df.empty:
        raise ValueError("Chat format not recognized. Try exporting again WITHOUT MEDIA.")

    # Clean unicode
    df['raw_date'] = df['raw_date'].str.replace("\u202f", " ").str.replace("\u202F", " ")

    # Parse datetime
    df['date'] = df['raw_date'].apply(smart_datetime_parser)

    # Remove rows that failed to parse
    df = df.dropna(subset=['date']).copy()

    # Separate user and message
    users = []
    msgs = []

    for m in df['user_message']:
        temp = re.split(r'^(.*?):\s', m, maxsplit=1)

        if len(temp) == 3:
            users.append(temp[1])
            msgs.append(temp[2])
        else:
            users.append("Group Notification aaya hai harsh")
            msgs.append(m)

    df['user'] = users
    df['message'] = msgs

    # Extract components
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time periods
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour+1}")

    df['period'] = period

    return df

