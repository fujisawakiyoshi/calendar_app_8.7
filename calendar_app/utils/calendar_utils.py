import calendar

def generate_calendar_matrix(year, month):
    """
    その月のカレンダーを2次元リストで返す
    例: [[0,0,1,2,3,4,5], [6,7,8,...], ...]
    """
    cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
    month_days = cal.monthdayscalendar(year, month)
    return month_days
