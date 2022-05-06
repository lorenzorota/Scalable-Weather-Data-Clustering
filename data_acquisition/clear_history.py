import datetime
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

PBCONFIG_PUBLISH_KEY = os.environ['PBCONFIG_PUBLISH_KEY']
PBCONFIG_SUBSCRIBE_KEY = os.environ['PBCONFIG_SUBSCRIBE_KEY']

pnconfig = PNConfiguration()
pnconfig.publish_key = PBCONFIG_PUBLISH_KEY
pnconfig.subscribe_key = PBCONFIG_SUBSCRIBE_KEY
pnconfig.uuid = "resetter-node"
pubnub = PubNub(pnconfig)

with open('cities.txt', 'r') as f:
    cities = f.read().splitlines()

def reset_channel(channel):
    now = int(datetime.datetime.today().timestamp()*1e7)

    envelope = pubnub.delete_messages()\
                     .channel(channel)\
                     .start(0)\
                     .end(now)\
                     .sync()

def delete_all():
    for city in cities:
        reset_channel(city)
    
if __name__ == '__main__':
    print('---------------------')
    print('Please read carefully')
    print('---------------------')
    print('You are about to delete all historic data that is distributed across all channels')
    confirmation = input('To proceed, enter \"see you later aligator\": ')
    if confirmation == "see you later aligator":
        delete_all()
        print('success!')
    else:
        print('goodbye!')