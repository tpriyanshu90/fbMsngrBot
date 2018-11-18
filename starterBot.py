import os
import time
import re
from slackclient import SlackClient
import random
from translate import Translator
# importing the requests library 
import requests
import json
# constants
from constants import *
# Modules for teaching the bot
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

chatbot = ChatBot('Motibot')
conv = open('chats.txt','r').readlines()
chatbot.set_trainer(ListTrainer)
chatbot.train(conv)

# chatbot = ChatBot(
#     'Priyanshu Tiwari',
#     trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
# )

# Train based on the english corpus
# chatbot.train("chatterbot.corpus.english")

#print(chatbot.get_response("Who is the founder of Google?"))

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def findISO(lang):
    """
        Finds ISO code for the given language
    """
    for isoLanguage in ISOLANGUAGES:
        if isoLanguage["name"] == lang.capitalize():
            return isoLanguage["code"]
    return None

def getTemp(cityName):
    """
        Function to find temp of the given city
    """
    PARAMS = {'address':cityName} 
    r = requests.get(url = "https://api.openweathermap.org/data/2.5/weather?q="+cityName+"&appid=6499100078bb92ae61e51355bc6f38db", params = PARAMS) 
    data = r.json()
    temp = data['main']['temp']
    weather = data['weather'][0]['main']
    return temp,weather

def handleFunction(command,func):
    """
        Function to calculate, Translate
    """
    try:
        # re.search(r"(?i)"+func,' '.join(SET_OF_FUNCTIONS))
        if("calculate" == func.lower()):
            func,command = command.split()
            try:
                return eval(command)
            except:
                return "Sorry! We are unable to calculate this expression."

        elif("translate" == func.lower()):
            command = re.split(r'\s',command)
            isoLan = findISO(command[len(command)-1])
            if isoLan == None:
                translation = "Sorry! we are unable to translate into this language"
                return translation
            translator= Translator(to_lang=isoLan)
            translation = translator.translate(' '.join(command[1:len(command)-2]))
            return translation

        elif("temperature" == func.lower() or "weather" == func.lower()):
            command = re.split(r'\s',command)
            cityName = (command[len(command)-1]).capitalize()
            temp = getTemp(cityName)
            if temp:
                temp_in_celcius = "It is "+str(round(temp[0]-273,2))+" C, "+temp[1]
                return temp_in_celcius
            return "Sorry we are unable to calculate temperature at this moment. Please try after sometime." 
        
        else:
            return None
    except:
        return None

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(random.choice(GREETINGS+QUESTIONS))

    # Finds and executes the given command, filling in response
    response = None

    # This is where you start to implement more commands!

    # Code for Greetings
    if re.search(r"(?i)"+command,' '.join(GREETINGS)):
      response = random.choice(GREETING_RESPONSES)

    # Code for QUESTIONS
    if re.search(r"(?i)"+command,' '.join(QUESTIONS)):
        response = random.choice(QUESTIONS_RESPONSES)

    # Performing various functions here
    func = re.split(r"\s",command)
    
    answer = None
    
    for i in SET_OF_FUNCTIONS:
        if(re.search(r"(?i)"+func[0],i)):
            answer = handleFunction(command,i)
            if answer:
                response = answer

    # Code for praisings
    if re.search(r"(?i)"+command," ".join(PRAISES)):
        response = random.choice(PRAISES_RESPONSE)

    if response==None:
        #Code for Quiz
        response = chatbot.get_response(command)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

#----------------------------------------MAIN PROGRAM---------------------------------------#
if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        # slack_client.api_call(
        # "chat.postMessage",
        # channel=CHANNEL_NAME,
        # text=WELCOME_MESSAGE
        # )

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")