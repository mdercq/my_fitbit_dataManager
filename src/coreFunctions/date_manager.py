import datetime
from datetime import timedelta

# def list_of_dates(date1, date2):
def list_of_dates():
    # for n in range(int((date2 - date1).days)+1):
    #     yield date1 + timedelta(n)
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1))
    today = datetime.datetime.now()
    return [yesterday, today]

