var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

function initmap() {
	// set up the map
	map = new L.Map('map');

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 15, attribution: osmAttrib});		

    // start the map in South-East England
    map.setView(new L.LatLng(19.433, -99.135), 13);
    map.addLayer(osm);
}


var iss;

function update_position() {
    $.getJSON('http://127.0.0.1:5000/static/bike_pos', function(data) {
        var latitude = data["bike_pos"]["latitude"];
        var longitude = data["bike_pos"]["longitude"];
        if (!iss) {
            iss = L.marker([latitude,longitude]).addTo(map);
        }
        setTimeout(update_position, 1000);
    });
}


