from flask import Flask, flash, render_template, request
from flask import url_for, make_response, redirect
import requests as re
import pandas as pd
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.secret_key = "super secret key"

def request_data(lat,lon):
    """
    insert lat/lon into meinprospekt api url and get response-object

    keywords:
    lat -- latitude in epsg4326
    lon -- longitude in epsg4326
    """
    url = 'http://www.meinprospekt.de/service/Map/getBranchMarkers?categoryId=5%2C2%2C%2C3&lat={}&lng={}&limit=5&web=1&version=2.0'.format(lat,lon)
    return re.get(url).json()['data']


def create_df_from_response(response):
    """
    create a dataframe from the response object and return

    keywords:
    response -- object returned by request_data()
    """
    df = pd.DataFrame(response)
    return df

    
def format_response_df(df):
    """
    format response df to match output format of name/street/zip/city

    keywords:
    df -- dataframe object from requests response
    """
    df = df[['merchantName', 'street', 'zip', 'city', 'lng', 'lat']].copy()
    df.columns = ['Name', 'StrNr', 'PLZ', 'Stadt', 'lon', 'lat']

    df.Name = ['Bio Company' if 'Bio Company' in x else x for x in df.Name]
    df.Name = ['Edeka' if 'EDEKA' in x else x for x in df.Name]
    df.Name = ['REWE' if 'Rewe' in x else x for x in df.Name]
    df.Name = ['REWE' if 'REWE' in x else x for x in df.Name]
    df.Name = ['Aldi' if 'ALDI' in x else x for x in df.Name]
    df.Name = ['Netto' if 'Netto' in x else x for x in df.Name]
    df.Name = ['Nahkauf' if 'Nahkauf' in x else x for x in df.Name]
    df.Name = ['E-Center' if 'E center' in x else x for x in df.Name]
    df.Name = ['Penny' if 'PENNY' in x else x for x in df.Name]
    df.Name = ["Kaiser's Tengelmann" if 'Tengelmann' in x else x for x in df.Name]
    df.Stadt = ['Berlin' if 'berlin' in x.lower() else x for x in df.Stadt]
    df = df[df.Name != "Kaiser's Tengelmann"]
    return df


def geocode_adress(adress):
    """
    take adress as input and geocode. 
    return lat lon of adress

    input: adress -- text
    """

    geocoder = Nominatim()
    location = geocoder.geocode(adress)
    return location
    

def make_csv_response(df):
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route('/', methods=['GET', 'POST'])
def index():
    error=None
    if request.method == 'POST':
        error = None
        # request form data on post
        lon = request.form['lon']
        lat = request.form['lat']
        adress = request.form['adress']

        if lon and lat:
            response = request_data(lat, lon)
            df = create_df_from_response(response)
            df = format_response_df(df)
            return make_csv_response(df)

        elif adress:
            location = geocode_adress(adress)
            try:
                response = request_data(location.latitude, location.longitude)
                df = create_df_from_response(response)
                df = format_response_df(df)
                return make_csv_response(df)
            except (KeyError, AttributeError):
                error='{} is not a valid adress'.format(adress)
                return render_template('shopstekt.html', error=error)
        
        elif lon and lat and adress:
            response = request_data(lat, lon)
            df = create_df_from_response(response)
            df = format_response_df(df)
            return make_csv_response(df)

        if not lon and not lat and not adress:
            error = 'either provide lat/lon or an adress'
            return render_template('shopstekt.html', error=error)

     # Render file input form
    return render_template('shopstekt.html')

 
# We only need this for local development.
if __name__ == '__main__':
    app.run()
