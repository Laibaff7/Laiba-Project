from flask import Flask, render_template, request, url_for
from datetime import datetime
from astropy.coordinates import get_body, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
import ephem
import math


app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html", image_url=url_for("static", filename="background/spaceimage.jpg")
    )


@app.route("/lunar")
def lunar():
    return render_template(
        "lunar.html", image_url=url_for("static", filename="background/spaceimage.jpg")
    )


@app.route("/planet")
def planet():
    return render_template(
        "planet.html", image_url=url_for("static", filename="background/spaceimage.jpg")
    )


@app.route("/calculate_lunar_phase", methods=["POST"])
def calculate_lunar_phase():
    date = request.form.get("date")
    if date == "":
        return render_template(
            "lunar.html",
            empty=True,
            image_url=url_for("static", filename="background/spaceimage.jpg"),
        )

    # Convert the provided date string to a datetime object
    datetime_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M")

    # Also create a formatted full date string from the above datetime object
    date = datetime_obj.strftime("%A, %d %B, %Y")

    # Create an ephem.Date object for the specified date
    ephem_date = ephem.Date(datetime_obj)

    # Calculate the lunar phase for the given date
    moon = ephem.Moon()
    moon.compute(ephem_date)
    illumination = round(moon.phase, 3)  # return percentage illumination
    phase = ""

    if round(illumination, 0) == 0:
        phase = "New Moon"
    elif round(illumination, 0) >= 1 and round(illumination, 0) <= 49:
        phase = "Waxing/Waning Crescent"
    elif math.trunc(illumination) == 50:
        phase = "First/Last Quarters"
    elif round(illumination, 0) >= 51 and round(illumination, 0) <= 99:
        phase = "Waxing/Waning Gibbous"
    elif round(illumination, 0) == 100:
        phase = "Full Moon"

    return render_template(
        "lunar.html",
        illumination=illumination,
        phase=phase,
        date=date,
        image_url=url_for("static", filename="background/spaceimage.jpg"),
    )


@app.route("/calculate_planet_positions", methods=["POST"])
def calculate_planet():
    date = request.form["date"]
    lat = request.form["latitude"]
    long = request.form["longitude"]

    if date == "" or lat == "" or long == "":
        return render_template(
            "planet.html",
            empty=True,
            image_url=url_for("static", filename="background/spaceimage.jpg"),
        )

    lat = float(lat)
    long = float(long)

    # Convert the provided date string to a datetime object
    datetime_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M")

    # Also create a formatted full date string from the above datetime object
    positions = planetary_positions(date, lat, long)

    date = datetime_obj.strftime("%A, %d %B, %Y")
    return render_template(
        "planet.html",
        result=positions,
        date=date,
        image_url=url_for("static", filename="background/spaceimage.jpg"),
    )


def planetary_positions(date, lati, long):
    # Set the observer's location
    observer_location = EarthLocation(lat=lati, lon=long)

    # Create an Astropy Time object for the specified date
    time = Time(date)

    # Calculate the positions of the planets
    planets = {
        "Mercury": get_body("mercury", time, observer_location),
        "Venus": get_body("venus", time, observer_location),
        "Mars": get_body("mars", time, observer_location),
        "Jupiter": get_body("jupiter", time, observer_location),
        "Saturn": get_body("saturn", time, observer_location),
        "Uranus": get_body("uranus", time, observer_location),
        "Neptune": get_body("neptune", time, observer_location),
    }

    positions = {}

    for planet_name, planet in planets.items():
        altaz = planet.transform_to(AltAz(location=observer_location, obstime=time))

        ra_hours = planet.ra.hms[0]
        ra_minutes = planet.ra.hms[1]
        ra_seconds = round(planet.ra.hms[2], 2)

        positions[planet_name] = {
            "azimuth": altaz.az.to(u.deg).value,
            "elevation": altaz.alt.to(u.deg).value,
            "right_ascension_hours": f"{ra_hours}h",  # (hr, mins, secs)
            "right_ascension_mins": f"{ra_minutes}mins",  # (hr, mins, secs)
            "right_ascension_secs": f"{ra_seconds}s",  # (hr, mins, secs)
            "declination": planet.dec.to(u.deg).value,
        }

    return positions


if __name__ == "__main__":
    app.run()
