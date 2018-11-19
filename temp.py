import re
import requests
import json
s = input()
ZODIAC_SIGNS = ["ARIES","TAURUS","GEMINI","CANCER","LEO","VIRGO","LIBRA","SCORPIUS","SAGITTARIUS","CAPRICORN","AQUARIUS","PISCES"] 
if re.search(r"(.)* ?horoscope ?(.)*",s,re.I):
	for sign in ZODIAC_SIGNS:
		if re.search(r'\b'+sign+r'\b',s,re.I):
			zodiac_sign = re.search(r'\b'+sign+r'\b',s,re.I).group(0)
			API_response = requests.get(url = "http://horoscope-api.herokuapp.com/horoscope/today/"+zodiac_sign)
			print(API_response.json()['horoscope'])

