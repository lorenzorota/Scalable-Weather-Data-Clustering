from datetime import datetime
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

PBCONFIG_SUBSCRIBE_KEY = os.environ['PBCONFIG_SUBSCRIBE_KEY']

pnconfig = PNConfiguration()
pnconfig.subscribe_key = PBCONFIG_SUBSCRIBE_KEY
pnconfig.uuid = "fetcher-node"
pubnub = PubNub(pnconfig)

with open('cities.txt', 'r') as f:
    cities = f.read().splitlines()

def get_data(channel, begin_date, end_date):
    out = []
    while True:
        envelope = pubnub.fetch_messages()\
                        .channels([channel])\
                        .maximum_per_channel(100)\
                        .start(begin_date)\
                        .end(end_date)\
                        .sync()
        res = envelope.result.channels

        channel = channel.replace(' ', '%20')
        if len(res) == 0:
            break
        else:
            messages = [item.message for item in res[channel]]
            for i, item in enumerate(res[channel]):
                messages[i]['timestamp'] = int(int(item.timetoken)//1e7)
            out += messages
            begin_date = int(res[channel][-1].timetoken)

    return out

if __name__ == '__main__':
    channel = input('city name: ')
    begin_date_str = input('begin date: ')
    end_date_str = input('end date: ')
    begin_date = datetime.fromisoformat(begin_date_str)
    end_date = datetime.fromisoformat(end_date_str)
    begin_date_ts = int(begin_date.timestamp()*1e7)
    end_date_ts = int(end_date.timestamp()*1e7)

    res = get_data(channel, begin_date_ts, end_date_ts)

    count = len(res)

    for i in range(count):
        print(res[i])

    print('-------------------------------')
    print('total: {} entries'.format(count))