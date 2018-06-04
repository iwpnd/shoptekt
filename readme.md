# shoptekt
  
flask app to download a csv of supermarkt POIs from [meinprospekt](http://meinprospekt.de)  
using lat/lon or adress as input

**keywords:**  
lat -- float ie. lat=52.1337  
lon -- float ie. lon=13.3337  
adress -- text ie. "Charlottenstraße 55-56, 10117 Berlin"

**output:**  
.csv with columns=['id', 'name', 'street', 'zip', 'city']  