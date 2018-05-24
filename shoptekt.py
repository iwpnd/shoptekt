from flask import Flask, flash, render_template, request
from flask import redirect, url_for, send_file
import requests as re
import pandas as pd

app = Flask(__name__)

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
    df = df[['merchantName', 'street', 'zip', 'city']].copy()
    df.columns = ['Name', 'StrNr', 'PLZ', 'Stadt']

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


@app.route('/api', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # catch args
        lon = float(request.args.get('lon'))
        lat = float(request.args.get('lat'))

        # get request response data, put it into a pandas
        # dataframe and format it as you wish
        response = request_data(lat,lon)
        df = create_df_from_response(response)
        df = format_response_df(df)

        # make_response object csv
        resp = make_response(df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp
     # Render file input form
    return render_template('shopstekt.html')

 
# We only need this for local development.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
