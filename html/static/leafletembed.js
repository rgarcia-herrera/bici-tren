var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

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


var bikeIcon = L.icon({
    iconUrl: 'bike-marker.png',
    iconSize:     [50, 70],
    iconAnchor:   [24, 69],

});

var bike_marker = false;

function update_position() {

    $.getJSON('http://127.0.0.1:5000/static/bike_pos', function(data) {
        var latitude = data["bike_pos"]["latitude"];
        var longitude = data["bike_pos"]["longitude"];
	console.log(latitude, longitude);
        if (!bike_marker) {
            bike_marker = L.marker([latitude,longitude],
				   {icon: bikeIcon}).addTo(map);
        } else {
	    bike_marker.setLatLng(new L.LatLng(latitude,
					       longitude));
	}
        setTimeout(update_position, 600);
    });
}


