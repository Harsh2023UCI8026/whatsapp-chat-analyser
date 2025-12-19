
# import re
# import pandas as pd
#
# def preprocess(data):
#
#     # Pattern for AM/PM WhatsApp date format
#     pattern = r'\d{2}\/\d{2}\/\d{2},\s+\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)\s+-'
#
#     messages = re.split(pattern, data)[1:]
#     dates = re.findall(pattern, data)
#
#     df = pd.DataFrame({
#         'user_message': messages,
#         'message_date': dates
#     })
#
#     # Fix Unicode narrow space
#     df['message_date'] = df['message_date'].astype(str).str.replace('\u202f', ' ', regex=False)
#
#     # Convert message_date → datetime
#     df['date'] = pd.to_datetime(
#         df['message_date'],
#         format='%d/%m/%y, %I:%M %p -',
#         errors='coerce'                      # Invalid dates become NaT instead of crashing
#     )
#
#     # Split user and message
#     users = []
#     msgs = []
#
#     for m in df['user_message']:
#         parts = re.split(r'^(.*?):\s', m, maxsplit=1)
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
#     # Extract date components (safe even if NaT exists)
#     df['year'] = df['date'].dt.year
#     df['month_num'] = df['date'].dt.month
#     df['month'] = df['date'].dt.month_name()
#     df['day'] = df['date'].dt.day
#     df['day_name'] = df['date'].dt.day_name()
#     df['only_date'] = df['date'].dt.date
#     df['hour'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute
#
#     # Create periods
#     period = []
#     for hour in df['hour']:
#         if pd.isna(hour):
#             period.append("NA")
#         elif hour == 23:
#             period.append("23-00")
#         elif hour == 0:
#             period.append("00-01")
#         else:
#             period.append(f"{hour}-{hour+1}")
#
#     df['period'] = period
#
#     return df
#

import re
import pandas as pd

def preprocess(data):

    # 🔥 Match BOTH formats:
    # 12-hour (AM/PM)  AND  24-hour
    pattern = r'\d{1,2}\/\d{1,2}\/\d{2,4},\s+\d{1,2}:\d{2}(?:\s?[APap][Mm])?\s+-'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({
        'user_message': messages,
        'raw_date': dates
    })

    # Fix WhatsApp hidden space (U+202F)
    df['raw_date'] = df['raw_date'].astype(str).str.replace('\u202f', ' ', regex=False)

    # ✅ AUTO-detect datetime format
    df['date'] = pd.to_datetime(
        df['raw_date'],
        errors='coerce'   # invalid → NaT (no crash)
    )

    # Drop rows where date couldn't be parsed
    df = df.dropna(subset=['date'])

    # Split user & message
    users = []
    msgs = []

    for m in df['user_message']:
        parts = re.split(r'^(.*?):\s', m, maxsplit=1)
        if len(parts) == 3:
            users.append(parts[1])
            msgs.append(parts[2])
        else:
            users.append("Group Notification aaya hai harsh")
            msgs.append(m)

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    # Date features
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time periods (for heatmap)
    df['period'] = df['hour'].apply(
        lambda h: f"{h}-{(h+1)%24}"
    )

    return df
