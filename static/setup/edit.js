const initial_lat = document.getElementById("latitude").value;
const initial_long = document.getElementById("longitude").value;

let map;
let marker = null;

if (initial_lat !== "0.0" || initial_long !== "0.0") {
    map = L.map('map', {
        center: [parseFloat(initial_lat), parseFloat(initial_long)],
        zoom: 15
    });
    updateMarker(L.latLng(parseFloat(initial_lat), parseFloat(initial_long)));
}
else {
    map = L.map('map', {
        center: [51.505, -0.09],
        zoom: 15
    });
    goToRealPosition()
}

map.on('click', onMapClick)

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

function goToRealPosition() {
    navigator.geolocation.getCurrentPosition(function(location) {
        map.flyTo([location.coords.latitude, location.coords.longitude], 15);
    });
}

function goToMarker() {
    if (marker === null) { return; }

    map.flyTo(marker.getLatLng(), 15);
}

function onMapClick(e) {
    updateMarker(e.latlng);
    document.getElementById("latitude").value = e.latlng.lat.toString();
    document.getElementById("longitude").value = e.latlng.lng.toString();
}

function onInputChange() {
    const latStr = document.getElementById("latitude").value;
    const lngStr = document.getElementById("longitude").value;
    updateMarker(L.latLng(parseFloat(latStr), parseFloat(lngStr)))
}

function updateMarker(latlng) {
    if (marker === null) {
        marker = L.marker(latlng).addTo(map);
    }
    else {
        marker.setLatLng(latlng);
    }
}


