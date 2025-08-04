import requests
import string
import debugpy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


import os

app = Flask(__name__)
app.config["DEBUG"] = True
# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)
# Use the instance folder for the SQLite database file
db_path = os.path.join(app.instance_path, "weather.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "thisisasecret"
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=b21a2633ddaac750a77524f91fe104e7"
    r = requests.get(url).json()
    # debugpy.breakpoint()
    return r


@app.route("/")
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)
        weather = {
            "city": city.name,
            "temperature": r["main"]["temp"],
            "description": r["weather"][0]["description"],
            "icon": r["weather"][0]["icon"],
        }
        weather_data.append(weather)

    return render_template("weather.html", weather_data=weather_data)


@app.route("/", methods=["POST"])
def index_post():
    err_msg = ""
    city_added = False
    new_city = request.form.get("city")
    if new_city:
        new_city = new_city.lower()
        new_city = string.capwords(new_city)
        # Normalize all city names in the database for comparison
        existing_city = City.query.filter(
            db.func.lower(City.name) == new_city.lower()
        ).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data["cod"] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
                city_added = True
            else:
                err_msg = "That is not a valid city!"
        else:
            err_msg = "City already exists in the database!"
    # If city_added is True, flash success. If not, and there is an error, flash error.
    if city_added:
        flash("City added successfully!", "success")
    elif err_msg:
        flash(err_msg, "error")
    # If city name is empty, do not flash anything (test expects silent ignore)
    return redirect(url_for("index_get"))


@app.route("/delete/<name>")
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f"Successfully deleted {city.name}!", "success")
    return redirect(url_for("index_get"))
