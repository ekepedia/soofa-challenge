# Location Tool

This is a web app created by intern Sandeep Sandwil over January, 2017 as part of an IAP externship. It allows users to explore the potential of different locations in a city for hosting a Soofa Sign by calculating metrics based on Google Maps, Yelp, and Walk Score data.

## Hosting

This app is hosted with Firebase and is owned by the devops@soofa.co account. Contact Ed Borden for more details. You can find it here: https://soofaiap.firebaseapp.com/

## Api Keys:
You will need a .env file in your local environment with api keys defined as the following:

yelp_ConsumerKey = Your Yelp ConsumerKey

yelp_ConsumerSecret = Your Yelp ConsumerSecret 

yelp_Token = Your Yelp Token

yelp_TokenSecret = Your Yelp Token Secret

google_API_KEY = Your Google Maps WEBSERVICE API Key

walkscore_api = Your Walk Score API key

You should also have the Google maps JAVASCRIPT api enabled for your Google key above. The WEBSERVICE api is used in the CreateHeatMaps.py script while the JAVASCRIPT api is used to generate addresses for markers in the web application. Once you activate the javascript api for your key, you can insert it into line 114 of HeatMap.html. 

````HTML
 <script src="https://maps.googleapis.com/maps/api/js?key=YOURAPIKEY&libraries=places"
  type="text/javascript"></script>
````

## How to Create Heatmaps:

You will first have to make sure your virtual environment is running python3. To make a virtual environment with python3, do 
````bash
virtualenv -p python3 envname
````
Then download all of the modules in requirements.txt. 
````bash
pip install -r /path/to/requirements.txt
````
Navigate to the directory that you are working in and enter the following into the command line:

```` bash
python3 CreateHeatMaps.py
````

Then, the following prompt will open: 

```` bash
Enter location in city, state format (NewHaven, CT): 
````

Enter the city that you wish to create heatmaps for. Note that depending on the size of the city, this may take 
anywhere from 15 minutes to multiple hours. Also, due to restrictions on the above apis, it is only possible to create heatmaps for 2-3  cities every day. Make sure that you have the walkscore.py file in the same folder. A small city that you can use for testing is Cuero, TX (typically takes 15 minutes to run). If the city is too large (more than a few hundred square miles in area), then it is likely that the api limits will not be enough to run the code for the city. Look at the error messages to see which api returned an error. You might need to buy a premium plan for that api. (This will most likely be the Google maps api).


## How to Visualize Heatmaps:

After CreateHeatMaps.py finishes, a file called 'SoofaDataYOURCITY.js' will be created in the DataFiles folder. Now open
HeatMap.html and search for id = "selectcity". There, you will need to add the following code to see the heatmaps for your city:

```` HTML
 <option value="Cityname">Cityname, State</option>
 ````

 Then, open HeatMap.html with Google Chrome. You will see a menu called 'Pick a City.' Click on this menu and then click on your city. This will update the map view and you will be able to see the heatmaps for your city by selecting from the 'Pick Heatmap Layers!' menu. Note: The current heatmap view is relative so once you zoom in/out of the map, the heatmap is regenerated. This means that a if you change how the map looks (zoom/move the map), the heatmap will also change. To change this, go to HeatMap.html and locate

 ````javascript
 var cfg1 = ...
 ````
 Then change cfg1.useLocalExtrema to false.

## How to use HeatMap.html:

You can select from a list of preloaded cities using the 'Cities' dropdown menu. The default city is Cambridge, MA. You can select which layers you want to see from the 'Show Layers' menu. If you want to see all the layers together, you can click on 'Show All Layers'.

You can also click on the map itself. This will create a draggable marker that you can move around. Dragging this marker will display the various scores for the marker location on the right side of the webpage. You can also have many markers at the same time. However, if you change cities, all the existing markers will be erased.

## How Scores are Calculated:

Each score ranges from 0 (low) to 10 (high). Each of the scores are relative and a score of 10 is given to the best location in the selected city. Each city is sampled with a grid of locations. The points of the grid are 500 meters apart from each other in both the x and y direction.

#### Google Scores:
Each of the Google scores measures the the number of particular types of buisnesses/locations that are in a 500 meter radious of a sampled grid point. 
For example, the Google food score measures the number of restaurants in your selected city. If you want to see the full list of location types that go into calculating The Google scores, go to CreateHeatMap.py and look at the following function:
````python
def getGoogleData(...) ...
````

The scores and then normalized to be between 0 and 10. Note that the Google API only returns at most 60 results for each search.


#### Yelp Scores:

The Yelp scores are calculated as follows. For each grid point, we sample 20 buisnesses/locations around the grid point that falls into a particular category (for example restaurants). Then for each of the 20 locations, we add up ratings^2 * # of ratings and the final sum is the score associated with the grid point. Finally, the scores are normalized to be between 0 and 10.

#### Walk Scores:
The walkscores are pulled from the walkscore API. For more information/methodology, see [here](https://www.walkscore.com/methodology.shtml).

The average score is just the average of all the other scores. It is also normalized to be between 0 and 10. The other scores provide much better information than the average score.

## Other Information:

The heatmaps are created using the Heatmap.js library. The map view is created using the leaflet.js library.
