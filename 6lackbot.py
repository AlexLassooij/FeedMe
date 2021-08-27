import json
import math
import slack
import os
import requests
import time
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import ssl
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from chromedriver_py import binary_path




env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

# Workaround for the ssl issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = slack.WebClient(token=os.environ['SLACK_TOKEN'], ssl=ssl_context)
BOT_ID = client.api_call("auth.test")['user_id']

places_key = os.environ['GOOGLE_PLACES_API_KEY']


@slack_event_adapter.on('message')
def message(payload):
    print(json.dumps(payload, indent=2))
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        if text == "joe" or 'Joe':
        
            client.chat_postMessage(channel=channel_id, text='mama')
        else:
            client.chat_postMessage(channel=channel_id, text=text)

#divider = slack.NewDividerBlock()

class configure_class:

    def __init__(self, food_type='', eat_out_type= '', user_budget=0, user_time=0, location=('49.25939', '-123.23876'), prev_location=('',''), restaurants={}):
        self.food_type = food_type
        self.eat_out_type = eat_out_type
        self.user_budget = user_budget
        self.user_time = user_time
        self.location = location
        self.prev_location = prev_location
        self.restaurants =restaurants

    def getLocation(self, view_id):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        timeout = 20
        driver = webdriver.Chrome(options=chrome_options, executable_path=binary_path)
        driver.get("https://mycurrentlocation.net/")
        wait = WebDriverWait(driver, timeout)
        longitude = driver.find_elements_by_xpath('//*[@id="longitude"]')
        longitude = [x.text for x in longitude]
        longitude = str(longitude[0])
        latitude = driver.find_elements_by_xpath('//*[@id="latitude"]')
        latitude = [x.text for x in latitude]
        latitude = str(latitude[0])
        driver.quit()
        if longitude and latitude:
            self.location = (longitude, latitude)
            print("location fetch successful")
        else :
            print("location fetch unsuccessful, using default location")
        print(self.location)
        loc_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={self.location[0]},{self.location[1]}&key={places_key}"

        payload = {}

        headers = {}

        res = requests.get(loc_url, headers=headers, data=payload)

        try:
            res.raise_for_status()
        except requests.exceptions as e:
                # Whoops it wasn't a 200
            print("Error: " + str(e))

        location = res.json().get('results')[0]['formatted_address']
        print(location)

        fetched_location_view = fetch_location_view
        fetched_location_view['blocks'][1]['text']['text'] = "📍 " + location

        print(fetched_location_view)

        updated_view = fetched_location_view
        client.views_update(view=updated_view, view_id=view_id)
        time.sleep(1.5)
        updated_view = get_eat_out_type_view
        client.views_update(view=updated_view, view_id=view_id)

    
    def fetchEateries(self):

        distance = int(self.user_time) * 100
        radius = "&radius=" + str(distance)
        type = "&type=restaurant"
        print(self.location)
        location = "location=" + self.location[0] + ',' + self.location[1]
        key = "&key=" + places_key
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?{location}{radius}{type}&opennow{key}" 

        payload = {}

        headers = {}

        res = requests.get(url, headers=headers, data=payload)
        

        try:
            res.raise_for_status()

        except requests.exceptions.HTTPError as e:
                # Whoops it wasn't a 200
            print("Error: " + str(e))

        print(res.text)

        restaurants = res.json().get('results')
        
        for restaurant in restaurants:
            location = restaurant.get('geometry').get('location')
            name = restaurant.get('name')
            rating = math.ceil(int(restaurant.get('rating'))) * ":star:"
            address = restaurant.get('vicinity')
            show_restaurants_view['blocks'].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{name}*\n{rating}\n{address}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Show in Maps",
                        },
                        "value": f"https://www.google.com/maps?q={location['lat']},{location['lng']}",

                        "action_id": "maps_link"
                    }
                    
                },
            )

        print(show_restaurants_view)

Configure_Food = configure_class()



# view definitions

configure_modal_initial_view = {
                        "type": "modal",
                        "callback_id": "food_configure_modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Let's eat !",
                        },
                        "blocks": [
                            {
                                "type": "divider",
                            },
                            {
                                "type": "section",
                                "block_id": "cook_order_selection_title",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Will you be cooking or eating out ?",
                                },
                            },
                            {
                                "type": "actions",
                                "block_id": "cook_order_selection",
                                "elements": [
                                        {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Cooking 👨‍🍳",
                                        },
                                        "action_id": "cook_food_button",
                                        "value": "cook",

                                        },
                                        {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Eating out 🏙",
                                        },
                                        "action_id": "order_food_button",
                                        "value": "no_cook",
                                        },
                                ]
                            },
                            {
                                "type": "section",
                                "block_id": "time_selection_title",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "How much time do you have ?",
                                },
                                "accessory": {
                                    "action_id": "time_select",
                                    "type": "static_select",
                                    "placeholder": {
                                        "type": "plain_text",
                                        "text": "Please Select"
                                    },
                                    "options": [
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "10 mins"
                                            },
                                            "value": "10",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "15 mins"
                                            },
                                            "value": "15",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "20 mins"
                                            },
                                            "value": "20",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "40 mins"
                                            },
                                            "value": "40",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "> 1 hour"
                                            },
                                            "value": "any",
                                        },
                                    ]
                                }
                            },
                            {
                                "type": "section",
                                "block_id": "budget_selection_title",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "What is your budget ($) ?",
                                },
                                "accessory": {
                                    "action_id": "budget_select",
                                    "type": "static_select",
                                    "placeholder": {
                                        "type": "plain_text",
                                        "text": "Please Select"
                                    },
                                    "options": [
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "5"
                                            },
                                            "value": "5",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "10"
                                            },
                                            "value": "10",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "15"
                                            },
                                            "value": "15",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "25"
                                            },
                                            "value": "25",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "> 40"
                                            },
                                            "value": "any",
                                        },
                                                               
                                    ]
                                }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "actions",
                                "elements": [
                                    {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Confirm",
                                        },
                                        "value": "confirm",
                                        "action_id": "confirm_initial"
                                    }
                                ]
                            } 
                        ]
                    }
    
get_eat_out_type_view = {
                        "type": "modal",
                        "callback_id": "food_configure_modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Let's eat !",
                        },
                        "blocks": [
                            {
                                "type": "divider",
                            },
                            {
                                "type": "section",
                                "block_id": "eat_out_selection_title",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "Would you like to order in or eat outside ?",
                                },
                            },
                            {
                                "type": "actions",
                                "block_id": "eat_out_selection",
                                "elements": [
                                        {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Ordering 🚗",
                                        },
                                        "action_id": "order_button",
                                        "value": "order",

                                        },
                                        {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Eating outside 🍽",
                                        },
                                        "action_id": "outside_button",
                                        "value": "eat_out",
                                        },
                                ]
                            },
                        ]
                    }
    
show_uber_options_view = {}

show_restaurants_view = {
                        "type": "modal",
                        "callback_id": "restaurant_options_modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Choose a restaurant",
                        },
                        "blocks": [
                            {
                                "type": "divider",
                            },
                            
                        ]
                    }

fetch_location_view = {
                        "type": "modal",
                        "callback_id": "food_configure_modal",
                        "title": {
                            "type": "plain_text",
                            "text": "Fetching your location",
                        },
                        "blocks": [
                            {
                                "type": "divider",
                            },
                            {
                                "type": "section",
                                "block_id": "fetch_location",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "📍",
                                },
                            },
                        ]
                    }
# handles interactions from app 

@app.route('/interaction', methods=['POST'])
def interaction():
    data = request.form
    payload = json.loads(data.get('payload'))
    action_value = payload.get('actions')[0].get('value')
    action_id = payload.get('actions')[0].get('action_id')
    view_id = payload.get('container').get('view_id')
  
    updated_view = {}
    # if food type, time and budget have been chosen, proceed to next menu

    if action_id == 'maps_link' :
        url = action_value
        webbrowser.open(url, new=2, autoraise=True)
    elif action_id == 'order_button':
    
        updated_view = show_uber_options_view
        print("showing uber options")
    elif action_id == 'outside_button' :
        print(Configure_Food.location)
        Configure_Food.fetchEateries()
        print("fetching restaurants")
        print("showing restaurants view")
        updated_view = show_restaurants_view
        client.views_update(view=updated_view, view_id=view_id)

    elif action_id == 'cook_food_button' or action_id == 'order_food_button':
        Configure_Food.food_type = action_value
        print(Configure_Food.food_type)
    elif action_id == 'time_select':
        action_value = payload.get('actions')[0].get('selected_option').get('value')
        Configure_Food.user_time = action_value
        print(Configure_Food.user_time)
        
    elif action_id == 'budget_select':
        action_value = payload.get('actions')[0].get('selected_option').get('value')
        Configure_Food.user_budget = action_value
        print(Configure_Food.user_budget)


    elif action_id == "confirm_initial" and Configure_Food.food_type and Configure_Food.user_budget and Configure_Food.user_time:
        if Configure_Food.food_type == 'no_cook':
            updated_view = fetch_location_view
            client.views_update(view=updated_view, view_id=view_id)
            print('fetching location')
            Configure_Food.getLocation(view_id)

            

        
                

    

    # client.views_update(view=configure_modal_budget, view_id=view_id)
    return Response(), 200


# handle imhungry command
# entry point for app
@app.route('/imhungry', methods=['POST', 'GET'])
def imhungry():
    data = request.form
    print(data)
    user_id = data.get('user_id')
    trigger_id = data["trigger_id"]
    channel_id = data.get('channel_id')
    text = data.get('text')



    
    # if text :
    #     client.chat_postMessage(channel=channel_id, text=text)
    #client.chat_postMessage(channel=channel_id, text="configure_payload")
    client.views_open(trigger_id=trigger_id, view=configure_modal_initial_view)


    return Response(), 200



if __name__ == "__main__":
    app.run(debug=True)