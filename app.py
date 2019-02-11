from flask import Flask, request, flash, redirect, render_template, request, url_for, session, g, abort
from random import randint
import os
import webbrowser
from functools import wraps
import speech_recognition as sr
import nltk
from nltk.tag.stanford import StanfordNERTagger
import json
import requests
import re
app = Flask(__name__)
@app.route("/")



def index():
    return render_template('index.html');

@app.route('/record/', methods=['GET'])

def record():
    recording = sr.Recognizer()
    with sr.Microphone() as source: 
        recording.adjust_for_ambient_noise(source)
        print("Please Say something:")
        audio = recording.listen(source)
    try:
        print(recording.recognize_google(audio))
    except Exception as e:
        print(e)
    
    
    
    synonyms = {
    "avanti": "avante",
    "avant": "avante",
    "avenger": "avante",
    "one day": "avante",
	"Avanti": "avante",
	"rent a": "avante"
    }
    compiled_dict = {}
    for value in synonyms:
        compiled_dict[value] = re.compile(r'\b' + re.escape(value) + r'\b')
    document = recording.recognize_google(audio)
    for value in compiled_dict:
        lowercase = compiled_dict[value]
        document = lowercase.sub(synonyms[value], document)
    with open("temp.txt", "w") as text_file:
        text_file.write(document)
    f = open('templates/text.html','w')

    content = """<html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- Bootstrap CSS -->
      <title>Clopay Configurator Screen</title>
    </head>
    <body>
        <div>
        <br>
        <br>
        <input type="button" value="Record" id="Record" onClick="parent.location='http://127.0.0.1:9002/record/'"/>
        <input type="text" value="{{ variable }}" id="SaySomething" style="font-size: 10pt; height: 40px; width:280px; "/> 
        <input type="button" value="Enter" id="Enter" onClick="parent.location='http://127.0.0.1:9002/enter/'"/>
        </div>
        
    </body>
    </html>"""
    f.write(content)
    f.close()

    return render_template('text.html', variable= recording.recognize_google(audio));

@app.route('/enter/', methods=['GET'])
def enter():

    java_path = "C:/Program Files/Java/jre1.8.0_191/bin"
    os.environ['JAVA_HOME'] = java_path

    file = open("temp.txt", "r") 
    sentence = file.read() 

    jar = './stanford-ner-tagger/stanford-ner.jar'
    model = './stanford-ner-tagger/dummy-ner-model-clopay.ser.gz'

    ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

    words = nltk.word_tokenize(sentence)
    list = ner_tagger.tag(words)
    DataDict = {val:key for (key, val) in dict(list).items()}
    del DataDict['0']

    url = 'http://dev-poc1.clopay.com/ClopaySSAPI/api/Collection/'
    payload = DataDict
    headers = {'content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    f = open('templates/result.html','w')

    content = """<html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- Bootstrap CSS -->
          <title>Clopay Configurator Screen</title>
    </head>
    <body>
        <div>
        <br> 
        <br> 
        <input type="button" value="Record" id="Record" onClick="parent.location='http://127.0.0.1:9002/record/'"/>
        <input type="text" id="SaySomething" style="font-size: 18pt; height: 40px; width:280px; "/> 
        <input type="button" value="Enter" id="Enter" onClick="parent.location='http://127.0.0.1:9002/enter/'"/>
        <br> 
        <br>
        Below are some results for query: {{variable2}}
        <br>
        <input type="text" value="{{ variable1 }}" id="JSON" style="font-size: 12pt; height: 120px; width:400px; "/>
        </div>
    </body>
    </html>"""

    f.write(content)
    f.close()
    return render_template('result.html', variable1= response.text, variable2 = sentence );
    
    
if __name__ == "__main__":

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True, host='0.0.0.0', port=9002)