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

    $.getJSON('http://127.0.0.1:5000/bike/59bd54a517a2952ed563a1c0', function(data) {
	console.log(data);
        var longitude = data["point"]["coordinates"][0];	
        var latitude = data["point"]["coordinates"][1];

        if (!bike_marker) {
            bike_marker = L.marker([latitude, longitude],
				   {icon: bikeIcon}).addTo(map);
        } else {
	    bike_marker.setLatLng(new L.LatLng(latitude,
					       longitude));
	}
        setTimeout(update_position, 600);
    });
}


var animated_marker = false;

function update_animation() {

    $.getJSON('http://127.0.0.1:5000/bike/59bd54a517a2952ed563a1c0',
	      function(data) {
		  var src = [data['point']['coordinates'][1],
			     data['point']['coordinates'][0]]
		  var dst = [data['predicted_point'][1],
			     data['predicted_point'][0]]
		  dst = [19.476827, -99.140168]
		  
		  var line = L.polyline([src, dst]);
					 
		  console.log(line);
		  
		  if (!animated_marker) {
		      animated_marker = L.animatedMarker(line.getLatLngs(),
							 {distance: data['speed'], // speed is m/s
							  interval: 1000,  // 1 sec
							  onEnd: update_animation});
		      animated_marker.setIcon(bikeIcon)
		      map.addLayer(animated_marker);
		  } else {
		      animated_marker.stop();
		      animated_marker.setLine(line.getLatLngs());
		      animated_marker.options.distance = data['distance'];
		      animated_marker.start();
		  }
		  // setTimeout(update_position, 600);
    });
}

