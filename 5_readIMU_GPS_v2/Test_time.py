import datetime

import pytz

time_pc_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
print(str(time_pc_now))
# tzone = datetime.timezone(datetime.timedelta(hours=8))
# utc_now = datetime.datetime.utcnow(tz=tzone).strftime('%H:%M:%S.%f')[:-3]
# print(utc_now)

dt_local = datetime.datetime.now()
utc_time = dt_local.astimezone(pytz.UTC)
time_to_ms = utc_time.strftime('%Y-%m-%d %H:%M:%S.%f')
print(utc_time)
print(time_to_ms)