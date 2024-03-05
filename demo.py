import requests
from flask import Flask, render_template, request,jsonify,redirect
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

app = Flask(__name__)

#database
client = MongoClient("mongodb+srv://admin1:9444571970aA@mycluster.rnws4sg.mongodb.net/mydb?retryWrites=true&w=majority")
db = client.weather
collection = db.users

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
                
                return redirect('/index')
        
        return redirect('/login')

    return render_template('login.html')


@app.route('/page1')
def Doc1():

  return render_template('signup.html')

curr_data = {}  # Global object to store current weather data

@app.route('/index', methods=['GET', 'POST'])
def weather():
    global curr_data
    
    if request.method == 'POST':
        api_key = 'dfb10abc1699424cabc4634e29564c4d'
        city = request.form.get('city')
        if city:
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                curr_data = {
                    'temperature': data['main']['temp'],
                    'condition': data['weather'][0]['main'],
                    'humidity': data['main']['humidity'],
                    'city': city,
                }
                return redirect(url_for('user'))
            else:
                return "Error fetching weather data. Please try again."
        else:
            return "City not provided in the form."
    else:
        if curr_data:
            return render_template('index.html', weather=curr_data)
        else:
            return render_template('index.html', weather=None)
      

@app.route('/user')
def user():
    global curr_data
    
    if curr_data:
        return render_template('index.html', weather=curr_data)
    else:
        return "No weather data available."

if __name__ == '__main__':
  app.run(debug=True,port=4500)