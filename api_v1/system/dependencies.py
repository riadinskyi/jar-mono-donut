import datetime

def get_one_month_ago()->int:
    today = datetime.datetime.now().date()
    result = today - datetime.timedelta(days=30)
    result=result.strftime("%s")
    return int(result)

