import requests
from flask import Flask, render_template, request,jsonify,redirect
from pymongo import MongoClient
from bson import ObjectId
import bcrypt


app = Flask(__name__)

openai_api_key = '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'
microsoft_api_key = '00301ef50emshf5d079849deb652p1225c9jsnf8b929db3d0f'

openai_url = "https://api.openai.com/v1/chat/completions"


microsoft_url = "https://microsoft-translator-text.p.rapidapi.com/translate"

def get_openai_response(user_query):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_query}],
        "temperature": 1.0,
        "top_p": 1.0,
        "n": 1,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    response = requests.post(openai_url, headers=headers, json=payload)
    response_json = response.json()
    return response_json['choices'][0]['message']['content']

def translate_text(text, source_lang='en', target_lang='ta'):
    print('source language query'+source_lang)
    print(target_lang)
    querystring = {
        "to[0]": target_lang,
        "api-version": "3.0",
        "from": source_lang,
        "profanityAction": "NoAction",
        "textType": "plain"
    }
    payload = [{"Text": text}]
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": microsoft_api_key,
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }
    response = requests.post(microsoft_url, json=payload, headers=headers, params=querystring)
    translation = response.json()[0]['translations'][0]['text']
    return translation


client = MongoClient("localhost",27017)
db = client.chatbot
collection = db.users
print("dfdffdfdfdfdf")
@app.route('/data')
def index():
    collection.find()
    res = []
    for d in data:
         d['_id'] = str(d['_id'])
         res.append(d)
       

    
    return jsonify(res)

###login and signup###
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print('ddddddddddddddddddd')
        email = request.form['email']
        password = request.form['password']

     
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

       
        if collection.find_one({'email': email}):
            return jsonify({'error': 'User already exists'})

        collection.insert_one({'email': email, 'password': hashed_password})

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = collection.find_one({'email': email})

        if user:
            
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                
                return redirect('/home')
        
        return jsonify({'error': 'Invalid email or password'})

    return render_template('login.html')





#for user query and response routes
@app.route('/home', methods=['GET', 'POST'])
def home():
    translated_text = None
    chat_response = None
    if request.method == 'POST':
        user_query = request.form['user_query']
        input_lang = request.form['input_lang']
        output_lang = request.form['output_lang']

        
        if input_lang != 'en':
            user_query = translate_text(user_query, source_lang=input_lang, target_lang='en')
            
            user_query = user_query+" give suitable indian law sections and what are the actions need to be taken for this situation"
           # print(user_query)

        chat_response = get_openai_response(user_query)

        
        
        if output_lang != 'en':
            translated_text = translate_text(chat_response, source_lang='en', target_lang=output_lang)
        else:
            translated_text = chat_response
            print(translated_text)
    return render_template('index.html', translated_text=translated_text, chat_response=chat_response)

if __name__ == '__main__':
    app.run(debug=True)
