from flask import render_template
from flask import redirect
from flask import request
from flask import Flask
import moodbot
import json
import os


app = Flask(__name__)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/api')
def api():
  return render_template('api.html', data=len(client.conversations))

@app.route('/api/response')
def api_response():
  query = request.args.get('query')

  # queries
  if request.args.get('search_range') != None: search_range = int(request.args.get('search_range'))
  else: search_range = 3
  if request.args.get('mode') != None: mode = request.args.get('mode')
  else: mode = 'random'
  if request.args.get('decimal') != None: decimal = int(request.args.get('decimal'))
  else: decimal = 3

  try:
    result = client.response(query, search_range=search_range, mode=mode, decimal=decimal)
  
    return {
      'content': result.content,
      'match': result.match,
      'confidence': result.confidence,
      'time': result.time
    }
  except:
    return {'success': False}

@app.route('/download')
def download():
  return render_template('download.html', data=os.listdir('data/'))

@app.route('/downloads')
def downloads():
  if os.path.exists(f'data/{request.args.get("file")}'):
    with open(f'data/{request.args.get("file")}', 'r') as file:
      return json.loads(file.read())

import nltk
nltk.download('punkt')

client = moodbot.chatbot()
client.train('data/rms-general.json', remove=['@', 'https://', ''], threshold=60)
client.train('data/scriptly-studios-general.json', remove=['@', 'https://', ''], threshold=60)

app.run(host='0.0.0.0', port=8080)
