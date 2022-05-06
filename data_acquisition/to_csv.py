from fetch_data import get_data
from datetime import datetime
import csv


if __name__ == '__main__':
    with open('cities.txt', 'r') as f:
        cities = f.read().splitlines()

    begin_date_str = input('begin date: ')
    end_date_str = input('end date: ')
    begin_date = datetime.fromisoformat(begin_date_str)
    end_date = datetime.fromisoformat(end_date_str)
    begin_date_ts = int(begin_date.timestamp()*1e7)
    end_date_ts = int(end_date.timestamp()*1e7)


    res = []
    for channel in cities:
        res += get_data(channel, begin_date_ts, end_date_ts)

    count = len(res)

    if count > 0:
        out_file = open("out.csv", "w")
        writer = csv.writer(out_file)
        writer.writerow(res[0].keys())
        for entry in res:
            if None in entry.values():
                continue
            else:
                writer.writerow(entry.values())
        out_file.close()