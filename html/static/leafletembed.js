var bike_id = document.currentScript.getAttribute('bike_id');
var map;

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




var bike_marker = false,
    dest_marker = false,
    bikeIcon = false;

var markers;
markers = new L.LayerGroup();

function update_position() {
    $.getJSON('http://127.0.0.1:5000/bike/' + bike_id, function(data) {

        dlong = data["destination"]["coordinates"][0];	
        dlat = data["destination"]["coordinates"][1];
        dest_marker = new L.Marker([dlat, dlong]);


        var longitude = data["point"]["coordinates"][0];	
        var latitude = data["point"]["coordinates"][1];
	bikeIcon = L.icon({
	    iconUrl: 'http://127.0.0.1:5000/bike/' + data['stamp'] +
		'/' + bike_id + '_marker.svg',
	    iconSize:     [50, 70],
	    iconAnchor:   [24, 69],
	});	
	bike_marker = new L.Marker([latitude, longitude],
				   {icon: bikeIcon});


	markers.clearLayers();
	dest_marker.addTo(markers);
	bike_marker.addTo(markers);
	markers.addTo(map);
        setTimeout(update_position, 1000);

    });
}
