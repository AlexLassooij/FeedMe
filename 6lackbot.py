import json
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
import ssl
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

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

    def __init__(self, food_type='', eat_out_type= '', user_budget=0, user_time=0):
        self.food_type = food_type
        self.eat_out_type = eat_out_type
        self.user_budget = user_budget
        self.user_time = user_time

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
                                                "text": "15 mins"
                                            },
                                            "value": "15",
                                        },
                                        {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "25 mins"
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

show_restaurants_view = {}
# handles any interactions

@app.route('/interaction', methods=['POST'])
def interaction():
    data = request.form
    payload = json.loads(data.get('payload'))
    action_value = payload.get('actions')[0].get('value')
    action_id = payload.get('actions')[0].get('action_id')
    view_id = payload.get('container').get('view_id')
    
    # print(payload.get('actions')[0])
    # print("action_id " + action_id)
    # print("value: " + action_value)

    # print("view_id: " + view_id)
    # print(type(view_id))
    #print(payload)
    # print(bool(-1))
    #print(bool(Configure_Food.food_type))
    # order_button outside_button
    updated_view = {}
    # if food type, time and budget have been chosen, proceed to next menu

    if action_id == 'order_button':
        if action_value == 'order':
            updated_view = show_uber_options_view
            print("showing uber options")
        else :
            updated_view = show_restaurants_view
            print("showing restaurants view")


    elif Configure_Food.food_type and Configure_Food.user_budget and Configure_Food.user_time:
        if Configure_Food.food_type == 'no_cook':
            
            if Configure_Food.eat_out_type == '' :
                updated_view = get_eat_out_type_view
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