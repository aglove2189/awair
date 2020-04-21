import os
import glob
import datetime
import pandas as pd
from awair import Awair


def read_csv(fp):
    try:
        return pd.read_csv(fp)
    except pd.errors.EmptyDataError:
        pass


if __name__ == "__main__":
    test_api = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiRFVNTVktSE9CQllJU1QifQ.hzjhIpGljqCZ8vCrOr89POy_ENDPYQXsnzGslP01krI"

    awair = Awair(test_api)

    os.makedirs("data", exist_ok=True)
    today = datetime.date.today()
    from_date = datetime.date(2019, 4, 9)
    to_date = from_date + datetime.timedelta(days=1)

    while to_date < today:
        fn = from_date.strftime("%m.%d.%Y")
        fp = f"data/{fn}.csv"
        if os.path.exists(fp):
            pass
        else:
            df = awair.get_sensor_df(from_date, to_date)
            df.to_csv(fp, index=False)

        from_date += datetime.timedelta(days=1)
        to_date += datetime.timedelta(days=1)

    # build out parquet
    df = pd.concat(map(read_csv, glob.glob('data/*.csv')))

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()

    df.to_parquet('data/awair.parquet')
