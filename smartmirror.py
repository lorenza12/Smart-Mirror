# file: smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

# https://github.com/KedarnathSahu/Smart-Mirror source

from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
import calendar_api
from datetime import datetime, timedelta
from random import randint
from user_settings import *

from PIL import Image, ImageTk
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()


with open("statements.json") as statements_file:
    statements = json.load(statements_file)
    

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=(clock_font, large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=(clock_font, small_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=(clock_font, small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.maxMin = ''
        self.maxTemp = ''
        self.minTemp = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=(weather_font, xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=(weather_font, medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.maxMinLbl = Label(self, font=(weather_font, small_text_size), fg="white", bg="black")
        self.maxMinLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=(weather_font, small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=(weather_font, small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:

            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()   #obsolete
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = weather_location
                
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]
            temperate_high = "%s%s" % (str(int(weather_obj['daily']['data'][0]['apparentTemperatureMax'])), degree_sign)
            temperate_low = "%s%s" % (str(int(weather_obj['daily']['data'][0]['apparentTemperatureMin'])), degree_sign)

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.maxTemp != temperate_high or self.minTemp != temperate_low:
                self.maxTemp = temperate_high
                self.minTemp = temperate_low
                
                
                self.maxMin = "High: " + self.maxTemp + "  Low: " + self.minTemp
                self.maxMinLbl.config(text=self.maxMin)
                
                
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)

        self.after(min_to_milli(weather_refresh), self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.rssCounter = 0 #start with google news
        self.title = "What's New" 
        self.newsLbl = Label(self, text=self.title, font=(news_font, medium_text_size, "underline"), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.get_headlines()

    def get_headlines(self):
        try:
            
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
                
            # cycle through each rss feed      
            headlines_url = rss_feeds[self.rssCounter]

            feed = feedparser.parse(headlines_url)

            post_count = 5
            for post in feed.entries:
                
                if (post_count == 0 ):
                    break
                else:
                     
                    # posts were running into calendar events so only grab shorter ones 
                    # this len can be changed to better suit your monitor width 
                    if (len(post.title) < 100):
                        headline = NewsHeadline(self.headlinesContainer, post.title)
                        headline.pack(side=TOP, anchor=W)
                        post_count -= 1

            # update counter so we get a new rss feed next time
            self.update_rssCounter()
                
            
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get news." % e)

        self.after(min_to_milli(news_refresh), self.get_headlines)
    
    def update_rssCounter(self):
        if self.rssCounter < len(rss_feeds) - 1:
            self.rssCounter += 1
        else:
            self.rssCounter = 0
            

class NewsHeadline(Frame):
    def __init__(self, parent, headline=""):
        Frame.__init__(self, parent, bg='black')
        
        # if the headline is blank don't add newpaper image
        if headline != "":
            image = Image.open("assets/Newspaper.png")
            image = image.resize((25, 25), Image.ANTIALIAS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            self.iconLbl = Label(self, bg='black', image=photo)
            self.iconLbl.image = photo
            self.iconLbl.pack(side=LEFT, anchor=N)

        self.headline = headline
        self.headlineLbl = Label(self, text=self.headline, font=(news_font, small_text_size), fg="white", bg="black")
        self.headlineLbl.pack(side=LEFT, anchor=N)


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLbl = Label(self, text=self.title, font=(news_font, medium_text_size, "underline"), fg="white", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.get_events()

    def get_events(self):
        # reference https://developers.google.com/google-apps/calendar/quickstart/python

        try:
            # remove all children
            for widget in self.calendarEventContainer.winfo_children():
                widget.destroy()
                
            end_date = datetime.utcnow() + timedelta(2) # get events within a 2-day span
            end_date = end_date.isoformat("T") + "Z" # Must be an RFC3339 timestamp for google api
                
            credentials = calendar_api.get_credentials()
            calendar_events = calendar_api.get_calendar_events(credentials,end_date,5)  # 5 events at most
            
            if calendar_events:
            
                for event in calendar_events:

                    event_start = event['start'].get('dateTime', event['start'].get('date'))
                    
                    #its a multiple day event - get the parts
                    if (event_start.find('T') != -1):  
                        try:
                            date_separator = event_start.find('T')
                            
                            event_day = event_start[:date_separator]
                            time_separator = event_start.find('-',date_separator)
                            
                            event_time_start =  event_start[date_separator+1:time_separator]
                            event_time_end = event_start[time_separator+1:]
                            
                            parsed_date = datetime.strptime(event_day,'%Y-%m-%d')
                            parsed_start_time = datetime.strptime(event_time_start,'%H:%M:%S')
                            parsed_end_time = datetime.strptime(event_time_end,'%H:%M')
                            
                            
                            if (time_format == 12):
                                #hour in 12h format
                                formated_start_time = datetime.strftime(parsed_start_time, '%I:%M') 
                                formated_end_time = datetime.strftime(parsed_end_time, '%I:%M')
                            else:
                                #hour in 24h format
                                formated_start_time = datetime.strftime(parsed_start_time, '%H:%M')
                                formated_end_time = datetime.strftime(parsed_end_time, '%H:%M')
                            
                            formated_start_date = datetime.strftime(parsed_date, date_format)
                            
                            event_string = event['summary'] + ' : '+ formated_start_date + ' - ' + formated_start_time + '-' +  formated_end_time 
                            
                        except Exception as e:
                            traceback.print_exc()
                            print ("Error: %s. Cannot get convert calendar times." % e)
    
                    else:
                    
                        try:
                            parsed_date = datetime.strptime(event_start,'%Y-%m-%d')
                            formated_start_date = datetime.strftime(parsed_date, date_format)
                            
                            event_string = event['summary'] + ' : ' + formated_start_date
                        
                        except Exception as e:
                            traceback.print_exc()
                            print ("Error: %s. Cannot get convert calendar times." % e)
                            
                    calendar_event = CalendarEvent(self.calendarEventContainer, event_string)
                    calendar_event.pack(side=TOP, anchor=E)
                    
            # else:
            #     calendar_event = CalendarEvent(self.calendarEventContainer, "- No Upcoming Events -")
            #     calendar_event.pack(side=TOP, anchor=E) 

        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get calendar events." % e)

        self.after(min_to_milli(calendar_refresh), self.get_events)
                
        
class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        image = Image.open("assets/Calendar.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)   
        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)
        
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=(calendar_font, small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)
     

        
class Statement(Frame):
    def __init__(self, statement ="What're you looking at?"):
        Frame.__init__(self)
        self.config(bg='black')
        self.statementText = statement
        self.statementLbl = ''
        self.get_statement()
        

    def get_statement(self):
        try:
            
            if (self.statementLbl != ''):
                self.statementLbl.destroy()
                
            # get current hour in 24 hour format    
            current_time = int(datetime.now().strftime('%H'))
            
            # randomly decide between greeting, quote, joke, or blank (1 in 4 chance to be pickd on update)
            statement_chance = randint(1,4)
            
            # quotes --- source: http://wisdomquotes.com/short-quotes/#shortdeathquotes
            if(statement_chance == 1):
                random_quote = randint(0,len(statements["quotes"]) - 1)                
                json_statement = fill_name(statements["quotes"][random_quote])
                
            # jokes --- source: https://chartcons.com/100-dumb-jokes-funny/
            elif (statement_chance == 2):
                random_joke = randint(0,len(statements["jokes"]) - 1)                
                json_statement = fill_name(statements["jokes"][random_joke])
              
            # greeting based on time  
            elif (statement_chance == 3):
                # between 5 am and 12 pm
                if (current_time > 5 and current_time < 12):

                    random_greeting = randint(0,len(statements["morning"]) - 1)
                    json_statement = fill_name(statements["morning"][random_greeting])

                # between 12 pm and 4 pm   
                elif (current_time > 12 and current_time < 16):

                    random_greeting = randint(0,len(statements["afternoon"]) - 1)                
                    json_statement = fill_name(statements["afternoon"][random_greeting])

                # between 7 pm and 8 pm
                elif (current_time > 19 and current_time < 20):

                    random_greeting = randint(0,len(statements["evening"]) - 1)                
                    json_statement = fill_name(statements["evening"][random_greeting])

                # between 8 pm and 12 am    
                elif (current_time > 20):

                    random_greeting = randint(0,len(statements["night"]) - 1)                
                    json_statement = fill_name(statements["night"][random_greeting])

                # between 5 pm and 7 pm
                else:
                    random_greeting = randint(0,len(statements["general"]) - 1)                
                    json_statement = fill_name(statements["general"][random_greeting])         
                    
            elif (statement_chance == 4):
                json_statement = ''
                          

        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get gretting." % e)
        
        
        
        self.statementText = json_statement
        self.statementLbl = Label(self, text=self.statementText, wraplength=1500, font=(statement_font, medium_text_size), fg="white", bg="black")
        self.statementLbl.pack(side=LEFT, anchor=N)
        
        self.after(min_to_milli(statement_refresh), self.get_statement)


class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.title("Smart Mirror")
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.centerFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.centerFrame.pack(anchor=CENTER, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        
        window_width = self.tk.winfo_screenwidth()
        window_height = self.tk.winfo_screenheight()
        
        screen_size = str(window_width) + "x" + str(window_height)
        
        self.tk.geometry(screen_size)  
        
        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=RIGHT, anchor=N, padx=50, pady=60)
        
        # calender 
        self.calender = Calendar(self.bottomFrame)
        self.calender.pack(side=RIGHT, anchor=E, padx=25, pady=60)
        
        # weather
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=50, pady=60)
        
        # news
        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=50, pady=60)
        
        # greeting, quote, or joke
        self.statement = Statement(self.centerFrame)
        self.statement.pack(anchor=CENTER, padx=50, pady=60)
        
        # change window icon
        self.tk.iconbitmap(icon_lookup['icon'])
        

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
