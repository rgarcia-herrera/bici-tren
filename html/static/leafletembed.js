var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

var bike_id = document.currentScript.getAttribute('bike_id');

function initmap() {
	// set up the map
	map = new L.Map('map');

	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 15, attribution: osmAttrib});

    // start the map someplace in Mexico
    map.setView(new L.LatLng(19.433, -99.135), 13);
    map.addLayer(osm);
}


// var bikeIcon = L.icon({
//     iconUrl: 'http://127.0.0.1:5000/bike/' + bike_id + '/marker',
//     iconSize:     [50, 70],
//     iconAnchor:   [24, 69],

// });


var bike_marker = false,
    dest_marker = false;

function update_position() {

    $.getJSON('http://127.0.0.1:5000/bike/' + bike_id, function(data) {

	var bikeIcon = L.divIcon({html:"<img src='/bike/" + bike_id + "_marker.svg' width='50px' />",
				  iconSize: [50, 70],
				  iconAnchor: [24, 69]});
	
        var dlong = data["destination"]["coordinates"][0];	
        var dlat = data["destination"]["coordinates"][1];
        if (!dest_marker) {	
            dest_marker = L.marker([dlat, dlong]).addTo(map);
	}
	
        var longitude = data["point"]["coordinates"][0];	
        var latitude = data["point"]["coordinates"][1];

        if (!bike_marker) {
            bike_marker = L.marker([latitude, longitude],
				   {icon: bikeIcon}).addTo(map);
        } else {
	    bike_marker.setLatLng(new L.LatLng(latitude,
					       longitude));
	}
        setTimeout(update_position, 500);
    });
}
