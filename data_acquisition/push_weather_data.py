# from multiprocessing.sharedctypes import Value
import aiohttp
import asyncio
import os
import sys, getopt
import signal
import logging
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from misc import Sleep


def keyboardInterrupt_handler():
    """ Safely exit event loop by setting an event and notifying tasks """

    print('Received keyboard interrupt signal, closing program.')
    event.set()
    sleep.cancel_all()

async def generate_new_weather_api_key(session):
    """ Regenerates the weather api key """

    global WEATHER_API_KEY
    payload={}
    headers = {'cookie': cookie}
    url = 'https://www.wunderground.com/key-gen/apikey/regenerate?apiKey={}'.format(WEATHER_API_KEY)
    async with session.post(url, headers=headers, data=payload) as resp:
        WEATHER_API_KEY = await resp.text()
        if await resp.text() == 'Given API key does not match profile key\n':
            raise ValueError('Weather API key could not be regenerated.')

async def get_sensor_list(session, url):
    """ Fetches the list of all available sensors for a city """

    async with session.get(url) as resp:

        # skip request if locked
        if lock.locked():
            return None

        try:
            if resp.status == 204:
                return None
            elif resp.status == 401:
                if not REGEN_KEY:
                    raise ValueError('Weather API key invalidated. Please provide a new one and restart the program.')
                logging.info('Weather API key invalidated. Generating new one...')
                async with lock:
                    await generate_new_weather_api_key(session)
                    logging.info('Using new API key.')
            data = await resp.json()
            pws_ids = data['location']['pwsId']
        except ValueError as err:
            print(err)
            exit(1)
        except Exception as err:
            print('Could not resolve query: {}. Error: {}'.format(url, resp.status))
            print(err)
            return None

        return pws_ids

async def get_sensor_data(session, url):
    """ Fetches all reported real-time data for a sensor """

    async with session.get(url) as resp:

            # skip request if locked
            if lock.locked():
                return None

            try:
                if resp.status == 204:
                    return None
                elif resp.status == 401:
                    if not REGEN_KEY:
                        raise ValueError('Weather API key invalidated. Please provide a new one and restart the program.')
                    logging.info('Weather API key invalidated. Generating new one...')
                    async with lock:
                        await generate_new_weather_api_key(session)
                        logging.info('Using new API key.')
                station_data = await resp.json()
            except ValueError as err:
                print(err)
                exit(1)
            except Exception as err:
                print('Could not resolve query: {}. Error: {}'.format(url, resp.status))
                print(err)
                return None
            
            return station_data

async def compute_avg_weather_data(session, url, city):
    """ Computes average sensor data and process the final weather data dictionary for a single city """

    tasks = []
    pws_ids = await get_sensor_list(session, url)

    if pws_ids is None:
        return None

    for idx, pws_id in enumerate(pws_ids):
        pws_url = 'https://api.weather.com/v2/pws/observations/current?stationId={}&format=json&units=e&apiKey={}'.format(pws_id, WEATHER_API_KEY)
        tasks.append(asyncio.ensure_future(get_sensor_data(session, pws_url)))

    station_data_list = await asyncio.gather(*tasks)

    latitudes = []
    longitude = []
    elevation = []
    solar_radiation = []
    uv = []
    winddir = []
    wind_chill = []
    wind_speed = []
    humidity = []
    temp = []
    pressure = []
    precip_rate = []

    if station_data_list is None:
        logging.info('List of station data is empty')
        return None
        
    for station_data in station_data_list:

        if station_data is None:
            # print('No station data was returned')
            continue

        latitudes.append(station_data['observations'][0]['lat'])
        longitude.append(station_data['observations'][0]['lon'])
        elevation.append(station_data['observations'][0]['imperial']['elev'])
        solar_radiation.append(station_data['observations'][0]['solarRadiation'])
        uv.append(station_data['observations'][0]['uv'])
        winddir.append(station_data['observations'][0]['winddir'])
        wind_chill.append(station_data['observations'][0]['imperial']['windChill'])
        wind_speed.append(station_data['observations'][0]['imperial']['windSpeed'])
        humidity.append(station_data['observations'][0]['humidity'])
        temp.append(station_data['observations'][0]['imperial']['temp'])
        pressure.append(station_data['observations'][0]['imperial']['pressure'])
        precip_rate.append(station_data['observations'][0]['imperial']['precipRate'])

    latitudes = [i for i in latitudes if i is not None]
    longitude = [i for i in longitude if i is not None]
    elevation = [i for i in elevation if i is not None]
    solar_radiation = [i for i in solar_radiation if i is not None]
    uv = [i for i in uv if i is not None]
    winddir = [i for i in winddir if i is not None]
    wind_chill = [i for i in wind_chill if i is not None]
    wind_speed = [i for i in wind_speed if i is not None]
    humidity = [i for i in humidity if i is not None]
    temp = [i for i in temp if i is not None]
    pressure = [i for i in pressure if i is not None]
    precip_rate = [i for i in precip_rate if i is not None]

    weather_data = {
        'city': city,
        'latitude' : None if len(latitudes) == 0 else float('{:.3f}'.format(sum(latitudes)/len(latitudes))),
        'longitude' : None if len(longitude) == 0 else float('{:.3f}'.format(sum(longitude)/len(longitude))),
        'elevation' : None if len(elevation) == 0 else float('{:.3f}'.format(sum(elevation)/len(elevation))),
        'solar_radiation' : None if len(solar_radiation) == 0 else float('{:.3f}'.format(sum(solar_radiation)/len(solar_radiation))),
        'uv' : None if len(uv) == 0 else float('{:.3f}'.format(sum(uv)/len(uv))),
        'winddir' : None if len(winddir) == 0 else float('{:.3f}'.format(sum(winddir)/len(winddir))),
        'wind_chill' : None if len(wind_chill) == 0 else float('{:.3f}'.format(sum(wind_chill)/len(wind_chill))),
        'wind_speed' : None if len(wind_speed) == 0 else float('{:.3f}'.format(sum(wind_speed)/len(wind_speed))),
        'humidity' : None if len(humidity) == 0 else float('{:.3f}'.format(sum(humidity)/len(humidity))),
        'temp' : None if len(temp) == 0 else float('{:.3f}'.format(sum(temp)/len(temp))),
        'pressure' : None if len(pressure) == 0 else float('{:.3f}'.format(sum(pressure)/len(pressure))),
        'precip_rate' : None if len(precip_rate) == 0 else float('{:.3f}'.format(sum(precip_rate)/len(precip_rate)))
    }

    return weather_data    

async def push_weather_data(session, city):
    """ Continuously pushes weather data for a single city every 10 seconds to the PubNub network """

    while True:
        # safely terminate task through interrupt handling
        if event.is_set():
            break

        url = 'https://api.weather.com/v3/location/search?query={}&locationType=locid&language=en-US&format=json&apiKey={}'.format(city, WEATHER_API_KEY)
        weather_data = await compute_avg_weather_data(session, url, city)
        if weather_data is None:
            logging.info('No weather data for city: {}'.format(city))
        else:
            logging.info('Processed weather data for city: {}'.format(city))

            # push to pubnub firehose api
            CHANNEL = city
            envelope = pubnub.publish().channel(CHANNEL).message(weather_data).sync()

            if envelope.status.is_error():
                logging.info("[PUBLISH: fail]")
                logging.info("error: %s" % envelope.status.error)
            else:
                logging.info("[PUBLISH: sent]")
                logging.info("timetoken: %s" % envelope.result.timetoken)

        await sleep.sleep(10)

async def run_event_loop():
    """ Asynchronously publish processed weather data for all provided cities in separate PubNub channels """

    connector = aiohttp.TCPConnector(force_close=True, limit=30)
    async with aiohttp.ClientSession(connector=connector) as session:

        tasks = []

        # load the cities
        for city in cities:
            print('Loaded city: {}'.format(city))
            tasks.append(asyncio.ensure_future(push_weather_data(session, city)))

        await asyncio.gather(*tasks, return_exceptions=True)

def main(argv):
    global REGEN_KEY, cookie, cities, lock, loop, event, sleep
    global pubnub, WEATHER_API_KEY, PBCONFIG_PUBLISH_KEY, PBCONFIG_SUBSCRIBE_KEY

    VERBOSE = False
    REGEN_KEY = False
    lock = asyncio.Lock()

    # parse arguments and options
    try:
        opts, args = getopt.getopt(argv,"hRV",["help", "verbose"])
    except getopt.GetoptError:
        print('invalid option')
        print('Try `python push_weather_data.py -h\' for more information.')
        sys.exit(2)

    # if opts == []:
    #     print('No options passed. Expected ')
    #     print('Try `python push_weather_data.py -h\' for more information.')
    #     sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('usage: ./push_weather_data.py [options]')
            print('-h or --help\t\t: displays information on options and arguments')
            print('-R or --regenkey\t: regenerate weather API key when it becomes invalid')
            print('-V or --verbose\t\t: display all information and debug messages')
            print()
            print('Environment variables:')
            print('WEATHER_API_KEY\t\t: the wunderground/weather API key')
            print('PBCONFIG_PUBLISH_KEY\t: the PubNub publish key')
            print('PBCONFIG_SUBSCRIBE_KEY\t: the PubNub subscribe key')
            exit()
        elif opt in ("-V", "--verbose"):
            VERBOSE = True
        elif opt in ("-R", "--regenkey"):
            REGEN_KEY = True
        
    if VERBOSE:
        logging.basicConfig(level=logging.INFO)

    # load info from text files
    try:
        with open('cookies.txt', 'r') as f:
            cookie = f.read()
    except FileNotFoundError:
        if REGEN_KEY:
            print('cookies.txt is missing')
            exit()

    with open('cities.txt', 'r') as f:
        cities = f.read().splitlines()

    WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
    PBCONFIG_PUBLISH_KEY = os.environ['PBCONFIG_PUBLISH_KEY']
    PBCONFIG_SUBSCRIBE_KEY = os.environ['PBCONFIG_SUBSCRIBE_KEY']

    pnconfig = PNConfiguration()
    pnconfig.publish_key = PBCONFIG_PUBLISH_KEY
    pnconfig.subscribe_key = PBCONFIG_SUBSCRIBE_KEY
    pnconfig.uuid = "publisher-node"
    pubnub = PubNub(pnconfig)

    sleep = Sleep()
    event = asyncio.Event()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, keyboardInterrupt_handler)
    loop.run_until_complete(run_event_loop())
    # asyncio.run(run_event_loop())

if __name__ == "__main__":
   main(sys.argv[1:])