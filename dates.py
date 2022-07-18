import datetime
def dateToString(date: datetime.datetime):
    return
date = datetime.datetime.now()
print(type(date))
date = datetime.datetime.strftime(date, "%Y-%m-%d")
print(date)