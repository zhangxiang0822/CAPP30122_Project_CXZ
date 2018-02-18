import json
import pandas as pd
import plotly as py
import plotly.graph_objs as graph_objs

#File from: 'http://catalog.civicdashboards.com/dataset/cda82e8b-7a8b-411e-95ba-1200b921c35d/resource/5c5d19a0-b817-49e6-b76e-ea63a8e2c0f6/download/fd880c1e4d23463ca869f1122109b3eftemp.geojson'
florida_data = pd.read_json('florida_shape.txt')

data = pd.read_csv("ACS_data.txt")
data['COUNTY'] = data['COUNTY'].astype(str)
data['state'] = data['state'].astype(str)

position1 = data['COUNTY'].str.len() == 1
position2 = data['COUNTY'].str.len() == 2
position3 = data['state'].str.len() == 1

data.loc[data['COUNTY'].str.len() == 1, 'COUNTY'] = '00' + data.COUNTY
data.loc[data['COUNTY'].str.len() == 2, 'COUNTY'] = '0' + data.COUNTY
data.loc[data['state'].str.len() == 1, 'COUNTY']  = '0' + data.state

data["Sex_ratio"] = data["Sex"]/data["Population"]
data.loc[data['Sex_ratio'] > 1, 'Sex_ratio'] = 1

subdata = data.loc[data['state'] == '12', :]

# Get county list
county_names = []
county_names_dict = {}

for county in florida_data['features']:
    for m in range(len(county['properties']['name'])):
        if county['properties']['name'][m:m+6] == 'County':
            county_names.append(county['properties']['name'][0:m-1])
            county_names_dict[county['properties']['name'][0:m-1]] = county['properties']['name']
            
print(county_names)

red_counties = []
blue_counties = []

for k, county in enumerate(county_names):
    for index, county_info in subdata.iterrows():
        county_name = county_info['NAME'].replace(" County, Florida", "").upper()
        if county.upper() == county_name:
            if county_info.Sex_ratio >=0.5:
                red_counties.append(florida_data['features'][k])
            else:
                blue_counties.append(florida_data['features'][k])

red_data = {"type": "FeatureCollection"}
red_data['features'] = red_counties

blue_data = {"type": "FeatureCollection"}
blue_data['features'] = blue_counties

with open('../../data/florida-red-data.json', 'w') as f:
    f.write(json.dumps(red_data))
with open('../../data/florida-blue-data.json', 'w') as f:
    f.write(json.dumps(blue_data))

init_notebook_mode(connected=True)

mapbox_access_token = "pk.eyJ1IjoieGlhbmd6aGFuZyIsImEiOiJjamRyb21jaWowZDkyMnhwN3Npc2lvOW1qIn0.oMqIu6FJJHPDcmTp7PJAOg"
py.tools.set_credentials_file(username='xiangzhang', api_key='zx930822')

data = graph_objs.Data([
    graph_objs.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
    )
])

layout = graph_objs.Layout(
    height=600,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        layers=[
            dict(
                sourcetype = 'geojson',
                source = 'florida-red-data.json',
                type = 'fill',
                color = 'rgba(163,22,19,0.8)'
            ),
            dict(
                sourcetype = 'geojson',
                source = 'florida-blue-data.json',
                type = 'fill',
                color = 'rgba(40,0,113,0.8)'
            )
        ],
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=27.8,
            lon=-83
        ),
        pitch=0,
        zoom=5.2,
        style='light'
    ),
)

fig = dict(data=data, layout=layout)

py.offline.iplot(fig, filename='county-level-choropleths-python')