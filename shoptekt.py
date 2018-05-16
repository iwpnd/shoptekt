from flask import Flask, request, make_response
import requests as re
import pandas as pd

app = Flask(__name__)
 

@app.route('/api', methods=['GET'])
def index():
    lon = float(request.args.get('lon'))
    lat = float(request.args.get('lat'))

    url = 'http://www.meinprospekt.de/service/Map/getBranchMarkers?categoryId=5%2C2%2C%2C3&lat={}&lng={}&limit=100&web=1&version=2.0'.format(lat,lon)
    response = re.get(url).json()['data']

    df = pd.DataFrame(response)
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

    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

 
# We only need this for local development.
if __name__ == '__main__':
    app.run(debug=True)
