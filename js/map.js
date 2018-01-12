/////////////// Base Map Setup /////////////////////////////
var baseLayer = L.tileLayer(
    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    }
);

var map = new L.Map(document.getElementById('map'), {
    center: new L.LatLng(42.3736, - 71.1097),
    zoom: 13,
    layers: [baseLayer]

});

map.on('click', onMapClick);

var baseMaps = {
    "Map View": baseLayer
};

/// Add Markers to Map on click, plus change scores when marker is dragged///
function onMapClick(e) {

    marker = new L.marker(e.latlng, {draggable:'true'});
    marker.on('click', markerOnClick);
    markercontainer.push(marker);

    for (var name in AllScores){
        document.getElementById(name).value = calculatescore(marker.getLatLng().lat,marker.getLatLng().lng, AllScores[name]);
    }

    var currlocation = geocodeLatLng(geocoder, marker.getLatLng().lat, marker.getLatLng().lng);

    marker.addTo(map)
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

        var currlocation = geocodeLatLng(geocoder, marker.getLatLng().lat, marker.getLatLng().lng);


        map.panTo(new L.LatLng(position.lat, position.lng))

    });

    map.addLayer(marker);
}

/// Update scores on click ///
function markerOnClick(e)
{
    for (var name in AllScores){
        document.getElementById(name).value = calculatescore(e.latlng.lat,e.latlng.lng, AllScores[name]);
    }

    var currlocation = geocodeLatLng(geocoder, e.latlng.lat, e.latlng.lng);

    map.panTo(new L.LatLng(e.latlng.lat, e.latlng.lng));
}

var cfg1 = {"radius": .007, "maxOpacity": .8, "scaleRadius": true, "useLocalExtrema": true, latField: 'lat', lngField: 'lng', valueField: 'count',  "blur": .8 };

var compositelayer = new HeatmapOverlay(cfg1);

/// Set Data ///
compositelayer.setData({max: 0, data:[]});

// /// Create Map Layers ///
var compositegroup = L.layerGroup([compositelayer]);

/// Add Layers to Map ///
map.addLayer(compositegroup);

var rect = L.rectangle([northeastcoord, southwestcoord], { dashArray: "10", color: "#4d4d4d",  opacity: .8,  fillOpacity: 0});
map.addLayer(rect);