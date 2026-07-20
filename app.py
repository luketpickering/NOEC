from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from noec_ws_server import InputProcessor
import json
import yaml

import os

app = Flask(__name__,
            static_url_path='', 
            static_folder='d3frontend',
            template_folder='d3frontend')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.from_mapping(
        SECRET_KEY='dev',
    )

wcInputProcessor = None

class Score(db.Model):
   id: Mapped[int] = mapped_column(primary_key=True)
   username: Mapped[str]
   score: Mapped[int]
   hist: Mapped[bool]
   noise: Mapped[bool]
   ml: Mapped[bool]
   slow_load: Mapped [bool]



def create_db(app):
   with app.app_context():
      db.create_all()

if not os.path.exists('db.sqlite'):
   create_db(app)
      

@app.route('/')
def home():
   return render_template('index.html')


@app.route('/web-controls')
def web_controls():
   global wcInputProcessor
   with open("ui_config.yaml", 'r') as yaml_in:
    uicfg = yaml.safe_load(yaml_in)
   wcInputProcessor = InputProcessor(uicfg)
   return render_template('webcontrols.html')

@app.route('/leaderboard')
def leaderboard():
   print(Score.__table__.columns)

   return render_template('leaderboard.html', scores =db.session.execute(db.select(Score).order_by(-Score.score)).scalars())

@app.route('/add_score',methods=['GET','POST'])
def add_score():
   if request.method == "POST":
      print("request", request.form)
      score = Score(username=request.form['username'], score=request.form['score'], hist=(request.form['hist']== 'true'),noise= (request.form['noise']== 'true'), ml=(request.form['ml']== 'true'), slow_load=(request.form['slow_load']== 'true'))
      db.session.add(score)
      db.session.commit()
   for row in db.session.execute(db.select(Score.username)):
      print(row)
   return '<p>Hello</p>'
   
@app.route('/update_input', methods=['POST'])
def update_input():
   global wcInputProcessor
   if request.method == "POST":
      inputDict = dict(request.form.lists())
      print(inputDict)
      processDict = { "ADCs": inputDict['ADCs[]'], "noise": inputDict['noise'] == ["true"], 'start_ml': inputDict["ml_start"] == ['true'], 'slow_load':inputDict['slow_load'] == ['true'], "states" :[0,0,0,0,0], "L_km": int(inputDict['L_km'][0]), "tick":0}
      print(processDict)
   return wcInputProcessor.process(processDict)


@app.route('/load_ui', methods=['POST'])
def load_ui():
   if request.method == "POST":
       with open("ui_config.yaml", 'r') as yaml_in:
          uicfg = yaml.safe_load(yaml_in)
       return  {"cmd": "ui_start", "cfg": uicfg}



if __name__ == '__main__':
   app.run(debug=True, port=8000)
