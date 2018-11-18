import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
import time
import re
from translate import Translator
import requests
import json
# constants
from constants import *
# Modules for teaching the bot
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

app = Flask(__name__)
ACCESS_TOKEN = 'EAAEx8zel9AIBANiZAlfM430LS7Gynj5x84dMLyTjsb62YS33pbzOMVvo8J9p5BM8A2MWDzPV0g0LrxEjqbR1xcoaU0lyNw91eUCoJVUKOAwSvGU1ZAgnWvUZAk72GIuy7dhnJfDt67Jg6r3ReZASGqkaGDKfpfcLddMhlN9stgZDZD'
VERIFY_TOKEN = 'awesomeWorked123986234'
bot = Bot(ACCESS_TOKEN)

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

#We will receive messages that Facebook sends our bot at this endpoint 

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
    	token_sent = request.args.get("hub.verify_token")
    	return verify_fb_token(token_sent)
    else:
    	output = request.get_json()
    	for event in output['entry']:
    		messaging = event['messaging']
    		for message in messaging:
    			if message.get('message'):
    				recipient_id = message['sender']['id']
    				if message['message'].get('text'):
    					response_sent_text = get_message(message['message'].get('text'))
    					send_message(recipient_id, response_sent_text)
    				if message['message'].get('attachments'):
    					response_sent_nontext = get_message()
    					send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

@app.route("/privacy_policy",methods=['GET','POST'])
def showPrivacy():
	if request.method =='GET':
		with open("privacy_policy") as fout:
			temp = fout.read()
	else:
		with open("privacy_policy") as fout:
			temp = fout.read()
	return temp

def verify_fb_token(token_sent):
	if token_sent == VERIFY_TOKEN:
		return request.args.get("hub.challenge")
	return 'Invalid verification token'

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

#chooses a random message to send to the user
def get_message(command):
	default_response = "Not sure what you mean. Try *{}*.".format(random.choice(GREETINGS+QUESTIONS))
	response = None
	if re.search(r"(?i)"+command,' '.join(GREETINGS)):
		response = random.choice(GREETING_RESPONSES)
	if re.search(r"(?i)"+command,' '.join(QUESTIONS)):
		response = random.choice(QUESTIONS_RESPONSES)
	func = re.split(r"\s",command)
	answer = None
	for i in SET_OF_FUNCTIONS:
		if(re.search(r"(?i)"+func[0],i)):
			answer = handleFunction(command,i)
			if answer:
				response = answer
	if re.search(r"(?i)"+command," ".join(PRAISES)):
		response = random.choice(PRAISES_RESPONSE)
	if response==None:
		response = chatbot.get_response(command)
	return str(response)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

# --------------------------------------------DRIVER PROGRAM---------------------------

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)