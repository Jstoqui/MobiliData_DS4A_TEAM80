import datetime
import pandas as pd
'''
dayofweek 	month 	dayofyear 	dayofmonth 	weekofyear
'''

datetime.timedelta()

def get_features(datetime_str):
    # datetime_str = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime_str.weekday(), datetime_str.month, datetime_str.timetuple().tm_yday, datetime_str.day, datetime_str.isocalendar()[1]

def get_feature_matrix(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    delta = end_date - start_date
    # print(delta)
    feat_mat = []
    dates = []
    for i in range(delta.days + 1):
        day = start_date + datetime.timedelta(days=i)
        # print(day)
        feat_mat.append(get_features(day))
        dates.append(day)

    df = pd.DataFrame(feat_mat, columns=["dayofweek", "month", "dayofyear", "dayofmonth", "weekofyear"], index=dates)
    return df
    


if __name__ == "__main__":
    start_str = "2017-06-06"
    end_str = "2017-06-20"

    print(get_feature_matrix(start_str, end_str))

    # datetime_str = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    # print(datetime_str.today().weekday()) # dayofweek
    # print(datetime_str.now().timetuple().tm_yday) # dayofyear
    # print(datetime_str.day)# dayofmonth
    # print(datetime_str.month)# month
    # print(datetime_str.isocalendar()[1])# weekofyear



