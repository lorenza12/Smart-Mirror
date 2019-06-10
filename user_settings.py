# file: user_settings.py
# description: a file to hold user settings and common functions

user_name = 'Al'
ui_locale = 'en_IN.UTF-8' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%B %d, %Y" # check python doc for strftime() for options
news_country_code = 'usa'
weather_api_token = '' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'auto' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = '41.881832' # Set this if IP location lookup does not work for you (must be a string)
longitude = '-87.623177' # Set this if IP location lookup does not work for you (must be a string)
weather_location = 'Chicago, IL' # Set this for the display

google_calendar_token = ""   # go to https://console.developers.google.com/ and register an app. Then search calendar in the search bar and enable calendar and get api
                                                                    # https://developers.google.com/calendar/quickstart/python instead

rss_feeds = ["https://news.google.com/rss?hl=" + news_country_code + "&gl=US&ceid=US:en", #add rss feed links here
             "https://www.cnet.com/rss/news/",
             "https://www.nasa.gov/rss/dyn/breaking_news.rss",
             "http://feeds.mashable.com/Mashable",
             "https://www.nasa.gov/rss/dyn/solar_system.rss"] 

# how often items refresh in minutes
calendar_refresh = 60
weather_refresh = 15
statement_refresh = 30
news_refresh = 15

#default_font = 'Helvetica'
default_font = 'Helvetica'

clock_font = 'Helvetica'
calendar_font = 'Tahoma'
weather_font = 'Helvetica'
statement_font = 'Segoe UI'
news_font = 'Segoe UI'

# font sizes
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18

# add additional icons here once they are placed in the assets directory
# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png",  # hail
    'icon': "assets/icon.ico"   # window icon
}



# Helper function to add name into greetins 
def fill_name(greeting):
    return greeting.replace('@NAME', user_name)

# Helper function to convert minutes to milliseconds
def min_to_milli(minute):
    return minute * 60000