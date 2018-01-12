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
