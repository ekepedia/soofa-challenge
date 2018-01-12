//// Google Reverse Geocodeing Setup (for address display) ////
var geocoder = new google.maps.Geocoder;

function geocodeLatLng(geocoder, lat, lng) {
    var latlng = {lat: lat, lng: lng};
    geocoder.geocode({'location': latlng}, function(results, status) {
        if (status === 'OK') {
            if (results[1]) {
                console.log(results[0]);
                document.getElementById('address').innerHTML = results[0].formatted_address.replace(",",",<br>");
            } else {
                document.getElementById('address').innerHTML = 'No results found';
            }
        } else {
            document.getElementById('address').innerHTML = 'Geocoder failed due to: ' + status;
        }
    });
}

/// Heatmap Specifications ///


/// If you want to have different colors, put this: gradient: {'.5': 'blue', '.8': 'red', '.95': 'white'}




//// Scoring Section ////

/// Get Scores of Closest Location ///
function closestscore (lat, lng, arr) {

    var bestlat = arr[0].lat;
    var bestlng = arr[0].lng;
    var bestdist = Math.pow(Math.abs(lat - bestlat), 2) + Math.pow(Math.abs(lng - bestlng), 2);
    var bestindex = 0;

    for (i = 1; i < arr.length; i++){
        currlat = arr[i].lat;
        currlng = arr[i].lng;
        currdist = Math.pow(Math.abs(lat - currlat), 2) + Math.pow(Math.abs(lng - currlng), 2);
        if (currdist < bestdist){
            bestlat = currlat;
            bestlng = currlng;
            bestindex = i;
            bestdist = currdist;
        }
    }
    return arr[bestindex].count
}

/// Return scores between 0 and 10 ///

function calculatescore(lat, lng, heatmapdata){
    score = closestscore(lat, lng, heatmapdata.data);
    return Math.round(1000*score/heatmapdata.max)/100; // Returns two decimal places
}

document.getElementById('selectcity').onchange = function(){
    var myScript = document.createElement('script');
    myScript.setAttribute('src', 'DataFiles/SoofaData' + this.value.split(" ")[0] + '.js');
    document.head.appendChild(myScript);
    myScript.onload = function() {
        compositelayer.setData({max:0, data: []});
        document.getElementById("layerselector").reset();
        map.panTo(new L.LatLng(lat, lng));
        for (var i = 0; i < markercontainer.length; i++){
            map.removeLayer(markercontainer[i]);
        };
        markercontainer = [];
        layersactive = [];
        map.removeLayer(rect);
        rect = L.rectangle([northeastcoord, southwestcoord], { dashArray: "10", color: "#4d4d4d",  opacity: .8,  fillOpacity: 0});
        map.addLayer(rect);
        for (var name in AllScores){
            document.getElementById(name).value = "";
        }
        document.getElementById('address').value = "";
    };

};


/// Function for adding multiple heatmaps together ///

function layertrigger(keyword){
    index = layersactive.indexOf(keyword);
    if (index > -1){
        layersactive.splice(index, 1);
    } else{
        layersactive.push(keyword);
    }
    if (layersactive.length > 0){
        var newdata = clone(AllScores[layersactive[0]].data);
        for (var j = 1; j < layersactive.length; j++){
            var adder = clone(AllScores[layersactive[j]].data);
            for (var i = 0; i < newdata.length; i++){
                newdata[i].count = newdata[i].count + adder[i].count;
            }
        }

        compositelayer.setData({max:1000, data: newdata});
    }

    else{
        compositelayer.setData({max: 0, data: []});
    }
}


/// Function to clone a javascript object ///

function clone(obj) {
    // Handle the 3 simple types, and null or undefined
    if (null == obj || "object" != typeof obj) return obj;

    // Handle Date
    if (obj instanceof Date) {
        var copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }

    // Handle Array
    if (obj instanceof Array) {
        var copy = [];
        for (var i = 0, len = obj.length; i < len; i++) {
            copy[i] = clone(obj[i]);
        }
        return copy;
    }

    // Handle Object
    if (obj instanceof Object) {
        var copy = {};
        for (var attr in obj) {
            if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
        }
        return copy;
    }

    throw new Error("Unable to copy obj! Its type isn't supported.");
}

var expanded = false;

function showCheckboxes() {
    var checkboxes = document.getElementById("checkboxes");
    if (!expanded) {
        checkboxes.style.display = "block";
        expanded = true;
    } else {
        checkboxes.style.display = "none";
        expanded = false;
    }
}

/// Code for Searchbox adding marker ///

var searchBox = new google.maps.places.SearchBox(document.getElementById('mapsearch'));
google.maps.event.addListener(searchBox, 'places_changed', function(){

    for (var i = 0; i < searchBox.getPlaces().length; i++){

        marker = new L.marker([searchBox.getPlaces()[i].geometry.location.lat(), searchBox.getPlaces()[i].geometry.location.lng()], {draggable:'true'});
        marker.on('click', markerOnClick);
        markercontainer.push(marker);

        for (var name in AllScores){
            document.getElementById(name).value = calculatescore(marker.getLatLng().lat,marker.getLatLng().lng, AllScores[name]);
        }

        var currlocation = geocodeLatLng(geocoder, marker.getLatLng().lat, marker.getLatLng().lng);

        marker.addTo(map);
        map.panTo(marker.getLatLng());

        marker.on('dragend', function(event){
            var marker = event.target;
            var position = marker.getLatLng();
            marker.setLatLng(new L.LatLng(position.lat, position.lng),{draggable:'true'});
            var currlocation = geocodeLatLng(geocoder, marker.getLatLng().lat, marker.getLatLng().lng);
            marker.addTo(map);


            for (var name in AllScores){
                document.getElementById(name).value = calculatescore(marker.getLatLng().lat,marker.getLatLng().lng, AllScores[name]);
            }

            document.getElementById('address').value = searchBox.getPlaces()[0].address;


            map.panTo(new L.LatLng(position.lat, position.lng))

        });
        map.addLayer(marker);
    }

});

/// Code for Showing/Hiding Scores ///

var theButton = document.getElementById('marker-icon');
var shown = false;
theButton.onclick = function() {
    if (shown){
        document.getElementById('sf-side-bar').style.height='50px';
        shown = !shown;
    }
    else{
        document.getElementById('sf-side-bar').style.height='350px';
        shown = !shown;
    }
};


var helpIcon = document.getElementById('help-icon');
var helpShown = false;
helpIcon.onclick = function() {
    console.log("S");
    if (helpShown){
        document.getElementById('sf-help-bar').style.height='50px';
        document.getElementById('sf-help-bar').style.width='50px';
        document.getElementById('sf-help-bar').style.padding='0';
        document.getElementById('help-icon').style.margin='15%';
        helpShown = !helpShown;
    }
    else{
        document.getElementById('sf-help-bar').style.width='250px';
        document.getElementById('sf-help-bar').style.padding='25px';
        document.getElementById('help-icon').style.margin='0%';
        document.getElementById('sf-help-bar').style.height='270px';
        helpShown = !helpShown;
    }
};

// Code for Dashed Recntangle //

