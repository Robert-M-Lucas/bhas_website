let map_zones;

if (initial_lat !== "0.0" || initial_long !== "0.0") {
    map_zones = L.map('map-zones', {
        center: [parseFloat(initial_lat), parseFloat(initial_long)],
        zoom: 15
    });
}
else {
    map_zones = L.map('map-zones', {
        center: [51.505, -0.09],
        zoom: 15
    });
    goToRealPosition()
}

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map_zones);

function goToRealPositionZones() {
    navigator.geolocation.getCurrentPosition(function(location) {
        map_zones.flyTo([location.coords.latitude, location.coords.longitude], 15);
    });
}

function goToMarkerZones() {
    if (marker === null) { return; }
    map_zones.flyTo(marker.getLatLng(), 15);
}

let zone_counter = 0;
let highest_index = 0;

const zone_template = document.getElementById("zone-template");
const zone_container = document.getElementById("zone-container");
function createZone(id, title, title_error, index, index_error,
                    start_time, end_time, time_error, circular,
                    internal_coordinate_error) {
    document.getElementById("no-zone-text").style.display = "none";

    let sid;
    if (id === null) {
        sid = "*" + zone_counter.toString();
        zone_counter += 1;
    }
    else {
        sid = id.toString();
    }

    if (index === null) {
        index = highest_index + 1;
        highest_index += 1;
    }
    else if (index > highest_index) {
        highest_index = index;
    }

    let new_zone = zone_template.cloneNode(true);
    // zone_container.insertBefore(new_zone, zone_container.firstChild);
    zone_container.appendChild(new_zone);
    new_zone.style.cssText = "";

    new_zone.id = "zone-" + sid;

    let zone_title_label = document.getElementById("title-zone-x-label");
    zone_title_label.id = "title-zone-" + sid + "-label";
    zone_title_label.for = "title-zone-" + sid;
    let zone_title = document.getElementById("title-zone-x");
    zone_title.name = zone_title.id = "title-zone-" + sid;
    zone_title.value = title;
    let zone_title_error = document.getElementById("title-zone-x-error");
    zone_title_error.id = "title-zone-" + sid + "-error";
    zone_title_error.for = "title-zone-" + sid;
    if (title_error !== null && title_error.length > 0) {
        zone_title_error.style.cssText = "";
        zone_title_error.innerText = title_error;
    }
    
    let zone_index_label = document.getElementById("index-zone-x-label");
    zone_index_label.id = "index-zone-" + sid + "-label";
    zone_index_label.for = "index-zone-" + sid;
    let zone_index = document.getElementById("index-zone-x");
    zone_index.name = zone_index.id = "index-zone-" + sid;
    zone_index.value = index.toString();
    let zone_index_error = document.getElementById("index-zone-x-error");
    zone_index_error.id = "index-zone-" + sid + "-error";
    zone_index_error.for = "index-zone-" + sid;
    if (index_error !== null && title_error.length > 0) {
        zone_index_error.style.cssText = "";
        zone_index_error.innerText = index_error;
    }
    
    let zone_start_time_label = document.getElementById("start-time-zone-x-label");
    zone_start_time_label.id = "start-time-zone-" + sid + "-label";
    zone_start_time_label.for = "start-time-zone-" + sid;
    let zone_start_time = document.getElementById("start-time-zone-x");
    zone_start_time.name = zone_start_time.id = "start-time-zone-" + sid;
    zone_start_time.value = start_time;
    let zone_end_time_label = document.getElementById("end-time-zone-x-label");
    zone_end_time_label.id = "end-time-zone-" + sid + "-label";
    zone_end_time_label.for = "end-time-zone-" + sid;
    let zone_end_time = document.getElementById("end-time-zone-x");
    zone_end_time.name = zone_end_time.id = "end-time-zone-" + sid;
    zone_end_time.value = end_time;
    let zone_time_error = document.getElementById("time-zone-x-error");
    zone_time_error.id = "time-zone-" + sid + "-error";
    zone_time_error.for = "end-time-zone-" + sid;
    if (time_error !== null && title_error.length > 0) {
        zone_time_error.style.cssText = "";
        zone_time_error.innerText = time_error;
    }

    let zone_circular_label = document.getElementById("circular-zone-x-label");
    zone_circular_label.id = "circular-zone-" + sid + "-label";
    zone_circular_label.for = "circular-zone-" + sid;
    let zone_circular = document.getElementById("circular-zone-x");
    zone_circular.name = zone_circular.id = "circular-zone-" + sid;
    zone_circular.checked = circular;

    let zone_show_label = document.getElementById("show-zone-x-label");
    zone_show_label.id = "show-zone-" + sid + "-label";
    zone_show_label.for = "show-zone-" + sid;
    let zone_show = document.getElementById("show-zone-x");
    zone_show.name = zone_show.id = "show-zone-" + sid;

    let zone_edit_label = document.getElementById("edit-zone-x-label");
    zone_edit_label.id = "edit-zone-" + sid + "-label";
    zone_edit_label.for = "edit-zone-" + sid;
    let zone_edit = document.getElementById("edit-zone-x");
    zone_edit.id = "edit-zone-" + sid;

    zone_edit.addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            startEditingZone(sid)
        }
    });

    if (internal_coordinate_error !== null) {
        let ic_error = document.getElementById("ic-zone-x-error");
        ic_error.id = "ic-zone-" + sid + "-error";
        ic_error.style.cssText = "";
    }

    let delete_button = document.getElementById("delete-zone-x");
    delete_button.id = "delete-zone-" + sid;
    delete_button.onclick = () => { deleteZone(sid); }
}

function deleteZone(sid) {
    document.getElementById("zone-" + sid).remove();
}

function showZone(sid) {}
function hideZone(sid) {}

let last_edited = null;
function startEditingZone(sid) {
    showZone(sid);
    document.getElementById("show-zone-" + sid).checked = true;

    if (last_edited !== null) { stopEditingZone(last_edited); }
    last_edited = sid;
}

function stopEditingZone(sid) {
    hideZone(sid);
    document.getElementById("show-zone-" + sid).checked = false;
}