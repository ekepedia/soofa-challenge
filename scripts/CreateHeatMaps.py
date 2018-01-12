################################## Python Script to Create City Heatmaps ############################################
import numpy as np
from datetime import datetime
import time
from functools import reduce

import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


start = time.time()

while True:
    city = input("Enter location in city, state format (NewHaven, CT): ")
    if len(city.split()) != 2:
        print("Sorry, enter the city as one name please")
        continue
    else:
        break



######################################################################## Yelp API Set Up ################################################################
import yelp
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
yelp_ConsumerKey = ' '
yelp_ConsumerSecret = ' '
yelp_Token = ' '
yelp_TokenSecret = ' '
yelp_ConsumerKey = os.environ.get('yelp_ConsumerKey') 
yelp_ConsumerSecret = os.environ.get('yelp_ConsumerSecret') 
yelp_Token = os.environ.get('yelp_Token') 
yelp_TokenSecret = os.environ.get('yelp_TokenSecret') 


auth = Oauth1Authenticator(consumer_key = yelp_ConsumerKey, consumer_secret = yelp_ConsumerSecret, token = yelp_Token, token_secret= yelp_TokenSecret)
client = Client(auth)



######################################################################## Google API Set Up ################################################################

import googlemaps

google_API_KEY = ' '

google_API_KEY = os.environ.get('google_API_KEY') 

gmaps = googlemaps.Client(key = google_API_KEY)	


######################################################################## Walscore API Set Up ################################################################

import walkscore

walkscore_api = ' '

walkscore_api = os.environ.get('walkscore_api') 

walkscore = walkscore.WalkScore(walkscore_api)




####### Calculates distance between two coordinates ##########
def CalculateDistance(coord1, coord2): # coord = {'lat' : latval, 'lng': longval}	
	
	Radius_miles = 3961
	
	lat1 = coord1['lat']
	lon1 = coord1['lng']
	
	lat2 = coord2['lat']
	lon2 = coord2['lng']
	
	lat1 = np.radians(lat1) 
	lon1 = np.radians(lon1)
	lat2 = np.radians(lat2)
	lon2 = np.radians(lon2)
	
	dlat = lat2 - lat1
	dlon = lon2 - lon1
	
	a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
	c = 2*np.arctan2(a**(.5), (1-a)**(.5))
	dm = c*Radius_miles
	
	return dm*1609.34  #Returns distance in meters 


######## Get Data from Yelp ############  

def getYelpData(xvals, yvals, num_xsamples, num_ysamples):
	food_tags = ['food']
	shop_tags = ['shopping']
	community_tags = ['parks', 'religiousorgs', 'education', 'publicservicesgovt']
	All_tags = {'yelpfoodData': food_tags, 'yelpshoppingData': shop_tags, 'yelpcommunityData': community_tags}
	scores = {}

	for tag_group in All_tags:
		scores[tag_group] = np.array([[0.0 for k in range(num_ysamples)] for k in range(num_xsamples)])
	
	for tag_group in All_tags:
		tag_list = All_tags[tag_group]
			
		for i in range(num_xsamples):
			for j in range(num_ysamples):
					
				lat = yvals[j]
				lng = xvals[i]

				for tag in tag_list:
					params = {'radius_filter': 500, 'category_filter': tag}
					result = client.search_by_coordinates(lat, lng, **params)
					for stores in result.businesses:
						scores[tag_group][i][j] += stores.review_count*stores.rating**2

	for tag_group in All_tags:
		if (np.amax(scores[tag_group]) > 0):
			scores[tag_group]= scores[tag_group]*10/np.amax(scores[tag_group])


	return((scores, All_tags))


############ Get Data from Google ###########

def getGoogleData(xvals, yvals, num_xsamples, num_ysamples):

	community_tags = ['library', 'church', 'school', 'laundry', 'post_office', 'gas_station']
	tourist_tags = ['amusement_park', 'aquarium', 'art_gallery', 'bowling_alley', 'museum', 'night_club', 'park', 'university', 'stadium', 'zoo']	  
	food_tags = ['restaurant']	   
	big_shops_tags = ['department_store', 'shopping_mall', 'clothing_store', 'shoe_store']
	small_shops_tags = ['florist', 'hair_care', 'bakery', 'book_store', 'liquor_store' , 'beauty_salon']
	transit_tags = ['transit_station']
	All_tags = {'googletransitData': transit_tags, 'googlecommunityData': community_tags, 'googletouristData': tourist_tags, 'googlefoodData': food_tags, 'googlebigshopsData': big_shops_tags, \
	   'googlesmallshopsData': small_shops_tags, 'googletransitData': transit_tags}
	scores = {}

	
	# Create a score array for all tag groups
	
	for tag_group in All_tags:
   		scores[tag_group] = np.array([[0.0 for k in range(num_ysamples)] for k in range(num_xsamples)])
	

	for tag_group in All_tags:
		tag_list = All_tags[tag_group]

		for i in range(num_xsamples):
			for j in range(num_ysamples):
				coord = {'lat': yvals[j], 'lng': xvals[i]}

				for tag in tag_list:
					curr_result = gmaps.places_nearby(location = coord, radius = 500, type = tag)
					places = curr_result['results']
					scores[tag_group][i][j] += len(places)


					if 'next_page_token' in curr_result:
						token = curr_result['next_page_token']
						time.sleep(5)
						curr_result = gmaps.places_nearby(location = coord, page_token = token)
						places = curr_result['results']
						scores[tag_group][i][j] += len(places)

						if 'next_page_token' in curr_result:
							token = curr_result['next_page_token']
							time.sleep(5)
							curr_result = gmaps.places_nearby(location = coord, page_token = token)
							places = curr_result['results']
							scores[tag_group][i][j] += len(places)

	for tag_group in All_tags:
		if (np.amax(scores[tag_group]) > 0):
			scores[tag_group]= scores[tag_group]*10/np.amax(scores[tag_group])


	return((scores, All_tags))



############ Get Data from Walkscore ###########

def getWalkscoreData(xvals, yvals, num_xsamples, num_ysamples):
	scores = np.array([[0.0 for k in range(num_ysamples)] for k in range(num_xsamples)])
	address = ''
	for i in range(num_xsamples):
		for j in range(num_ysamples):
			lat = yvals[j]
			lon = xvals[i]
			try:
				scores[i][j] = walkscore.makeRequest(address, lat, lon)['walkscore']
			except:
				scores[i][j] = 0.0
	All_tags = {'walkscoreData': []}

	scores = scores*10/np.amax(scores)
	walkscores = {'walkscoreData': scores}

	return((walkscores, All_tags))




########### Turn a matrix of scores into javascript code #############

def javascriptwriter(scores, xvals, yvals, num_xsamples, num_ysamples, All_tags):
    output = ""
    for tag_group in All_tags:
        Best = np.amax(scores[tag_group])
        output += " var %s ={max: %f, data: [" % (tag_group, Best)
        for i in range(num_xsamples):
            for j in range(num_ysamples):
                output += "{lat: %.10f, lng: %.10f, count: %.10f}," %(yvals[j], xvals[i], scores[tag_group][i][j]) 

        output = output[:-1]
        output += "]}; "
        output += "\n"

    return (output)



######## Set up coordinate grid ###########################

sampling_rate = 500      # Sample every 500 meters in both x and y directions
city_geocode = gmaps.geocode(city)	 # Get city bounding coordinates
northeast_coord = city_geocode[0]['geometry']['bounds']['northeast']	   # NorthEast coordinates 
southwest_coord = city_geocode[0]['geometry']['bounds']['southwest']	   # SouthWest coordinates
center_coord = city_geocode[0]['geometry']['location']
southeast_coord = {'lat': southwest_coord['lat'], 'lng': northeast_coord['lng']}
xdist = CalculateDistance(southwest_coord, southeast_coord)	   # x distance of bounding box in meters
ydist = CalculateDistance(northeast_coord, southeast_coord)	   # y distance of bounding box in meters 
num_xsamples = int(np.round(xdist/sampling_rate))
num_ysamples = int(np.round(ydist/sampling_rate))
xvals = np.linspace(southwest_coord['lng'], southeast_coord['lng'], num_xsamples)   # x values (longitudes) that will be sampled
yvals = np.linspace(southeast_coord['lat'], northeast_coord['lat'], num_ysamples)   # y vals (latitudes) that will be sampled
# print('Estimated Time to finish: %f Minutes' %(num_xsamples*num_ysamples*.17))    # Prints estimated time till completion, not very accurate


############ Get the heatmaps ############
print('Starting Yelp Calculations')
try:
    yelpscores, yelptags  = getYelpData(xvals, yvals, num_xsamples, num_ysamples)
    outputyelp = javascriptwriter(yelpscores, xvals, yvals, num_xsamples, num_ysamples, yelptags)
    f = open('SoofaData' + city.split(",")[0] + 'yelpdata' + '.js', "w")  # Save data as you go along
    f.write(outputyelp + '\n')
    f.close()
    print('Done with Yelp!')
except:
    outputyelp = ""
    print('Sorry, yelp did not complete. \n')

print('Starting Walk Score Calculations')

try:
    walkscores, walktags = getWalkscoreData(xvals, yvals, num_xsamples, num_ysamples)
    outputwalkscore = javascriptwriter(walkscores, xvals, yvals, num_xsamples, num_ysamples, walktags)
    f = open('SoofaData' + city.split(",")[0] + 'walkscoredata' + '.js', "w") # Save data as you go along
    f.write(outputwalkscore + '\n')
    f.close()
    print('Done with Walkscore!')
except:
    outputwalkscore = ""
    print('Sorry, walkscore did not complete. \n')


print('Starting Google Calculations (This might take a long time.)')
try:
    googlescores, googletags = getGoogleData(xvals, yvals, num_xsamples, num_ysamples)
    outputgoogle = javascriptwriter(googlescores, xvals, yvals, num_xsamples, num_ysamples, googletags)
    f = open('SoofaData' + city.split(",")[0] + 'googledata' + '.js', "w") # Save data as you go along
    f.write(outputgoogle + '\n')
    f.close()
    print('Done with google!')
except:
    outputgoogle = ""
    print('Sorry, google did not complete.\n')

try:

	print('Calculating Averge Data')

	AllScores = [yelpscores, walkscores, googlescores]
	AllResults = []

	for score in AllScores:
		AllResults.extend(score.values())

	AvgResult = reduce((lambda x, y: np.add(x,y)), AllResults)
	AvgScore = {'averageData': AvgResult/len(AllResults)}
	AvgTags = {'averageData' : []}
	averageData = javascriptwriter(AvgScore, xvals, yvals, num_xsamples, num_ysamples, AvgTags)

except:

	print('Sorry, average data could not be calculated')
	averageData = ""


############ Save the heatmap data ############

print('Writing Data into File')
try:  # If DataFiles is a valid subfolder
	f = open('DataFiles/SoofaData' + city.split(",")[0] + '.js', "w")
	f.write(outputyelp + '\n')
	f.write(outputwalkscore + '\n')
	f.write(averageData + '\n')
	f.write(outputgoogle + '\n')
	f.write('var lat = ' + str(center_coord['lat']) + '\n')
	f.write('var lng = ' + str(center_coord['lng']) + '\n')
	f.write('var AllScores = {"googlefood": googlefoodData, "googlecommunity": googlecommunityData, "googlebigshops": googlebigshopsData, "googlesmallshops": googlesmallshopsData, "googletourist": googletouristData, "googletransit": googletransitData, "yelpfood": yelpfoodData, "yelpshopping": yelpshoppingData, "yelpcommunity": yelpcommunityData, "walkscore": walkscoreData, "average": averageData};' + '\n')
	f.write('var northeastcoord = [' + str(northeast_coord['lat']) + ',' + str(northeast_coord['lng']) + ']; \n')
	f.write('var southwestcoord = [' + str(southwest_coord['lat']) +  ',' + str(southwest_coord['lng']) + ']; \n')
	f.close()
	print('Writing Finished!')
	print('Minutes taken: %f' %((time.time() - start)/60.0))
except:
	f = open('SoofaData' + city.split(",")[0] + '.js', "w")
	f.write(outputyelp + '\n')
	f.write(outputwalkscore + '\n')
	f.write(averageData + '\n')
	f.write(outputgoogle + '\n')
	f.write('var lat = ' + str(center_coord['lat']) + '\n')
	f.write('var lng = ' + str(center_coord['lng']) + '\n')
	f.write('var AllScores = {"googlefood": googlefoodData, "googlecommunity": googlecommunityData, "googlebigshops": googlebigshopsData, "googlesmallshops": googlesmallshopsData, "googletourist": googletouristData, "googletransit": googletransitData, "yelpfood": yelpfoodData, "yelpshopping": yelpshoppingData, "yelpcommunity": yelpcommunityData, "walkscore": walkscoreData, "average": averageData};' + '\n')
	f.write('var northeastcoord = [' + str(northeast_coord['lat']) + ',' + str(northeast_coord['lng']) + ']; \n')
	f.write('var southwestcoord = [' + str(southwest_coord['lat']) +  ',' + str(southwest_coord['lng']) + ']; \n')
	f.close()
	print('Writing Finished!')
	print('Minutes taken: %f' %((time.time() - start)/60.0))


