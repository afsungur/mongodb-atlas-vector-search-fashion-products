var accessTokenMapBox = 'pk.*******uSA'
var filtermap = null;
var markerFilterGroup = null;
var circleFilterGroup = null; 
var rectangleLayerGroup = null;
var polygonLayerGroup = null;
var polygonLayerGroup2 = null;
var markerFilterGroup2 = null;
var polygonLayerGroup3 = null;
var markerFilterGroup3 = null;
var isItFor2NDPolygon = false;
var markerResultsFilterGroup = null;



var greenIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
    });


function initMap(shape) {

    if (filtermap !== null ) {
        filtermap.remove()
    }
    filtermap = L.map('mapid').setView([41.42, 2.20], 9);
    circleFilterGroup = L.featureGroup();
    markerFilterGroup = L.featureGroup();
    rectangleLayerGroup = L.featureGroup();
    polygonLayerGroup = L.featureGroup();
    markerFilterGroup2 = L.featureGroup(); // 2nd marker group in polygon
    polygonLayerGroup2 = L.featureGroup(); // 2nd polygon
    markerResultsFilterGroup = L.featureGroup();
    filtermap.addLayer(circleFilterGroup)
    filtermap.addLayer(markerFilterGroup)
    filtermap.addLayer(markerFilterGroup2)
    filtermap.addLayer(rectangleLayerGroup)
    filtermap.addLayer(polygonLayerGroup)
    filtermap.addLayer(polygonLayerGroup2)
    filtermap.addLayer(markerResultsFilterGroup)

    
    if (shape === "Circle") {
        filtermap.on('click', function(e) {
            addCircleMarker(e.latlng)
        })
    }
    else if (shape === "Box") {
        filtermap.on('click', function(e) {
            addBoxMarker(e.latlng)
        })
    }
    else if (shape === "Polygon") {
        filtermap.on('click', function(e) {
            addPolygonMarker(e.latlng)
        })
    }   

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: accessTokenMapBox
    }).addTo(filtermap);
}

function addCircleMarker(latlng) {
    markerFilterGroup.clearLayers()
    circleFilterGroup.clearLayers()
    var marker = L.marker(latlng).addTo(markerFilterGroup);
}

function addBoxMarker(latlng) {
    let marker_arr = []
    markerFilterGroup.eachLayer(function(layer) {
        marker_arr.push(layer.getLatLng())
    })
    if (marker_arr.length == 2) { alert("You can add 2 markers, if you want to re-draw rectangle, clear the map!"); return false; }

    var marker = L.marker(latlng).addTo(markerFilterGroup);
    marker_arr.push(marker.getLatLng())
    if (marker_arr.length == 2) {
        // draw rectangle
        var bounds = marker_arr;
        L.rectangle(bounds, {color: "#ff7800", weight: 2, fillOpacity:0.5}).addTo(rectangleLayerGroup);
    }
}

function addPolygonMarker(latlng) {
    if ( isItFor2NDPolygon ) { 
        addPolygonMarker2(latlng)
    } else {
        polygonLayerGroup.clearLayers()

        var marker = L.marker(latlng).addTo(markerFilterGroup);

        let count=0
        let marker_arr=[]
        markerFilterGroup.eachLayer(function(layer) {
            marker_arr.push(layer.getLatLng())
        })
        if (marker_arr.length >= 3) {
            var bounds = marker_arr;
            L.polygon(bounds, {color: "#ff7800", weight: 2, fillOpacity:0.5}).addTo(polygonLayerGroup);
        }
    }
}

function addPolygonMarker2(latlng) {
    polygonLayerGroup2.clearLayers()

    var marker = L.marker(latlng).addTo(markerFilterGroup2);
    
    let count=0
    let marker_arr=[]
    markerFilterGroup2.eachLayer(function(layer) {
        marker_arr.push(layer.getLatLng())
    })
    if (marker_arr.length >= 3) {
        var bounds = marker_arr;
        L.polygon(bounds, {color: "#ff7800", weight: 2, fillOpacity:0.5}).addTo(polygonLayerGroup2);
    }
}

function addResultMarkers(results) {

    $.each(results, function(index, item) {
        // console.log(item.address.location.coordinates)
        // switching longtitude latitude, leaflet requires latitude first, Atlas returns longtitude first
        coord_array= []
        coord_array[0] = item.address.location.coordinates[1]
        coord_array[1] = item.address.location.coordinates[0]
        var marker = L.marker(coord_array, {icon: greenIcon}).addTo(markerResultsFilterGroup);
        
        marker.bindPopup("<b>Street:</b>"+item.address.street +"<br/><b>Name:</b>" + item.name +'<br/>').openPopup()
    });
}


var placeholder_description = $('#description_text');
function addResultMarkersNear(results) {
    $.each(results, function(index, item) {
        // console.log(item.address.location.coordinates)
        // switching longtitude latitude, leaflet requires latitude first, Atlas returns longtitude first
        coord_array= []
        coord_array[0] = item.address.location.coordinates[1]
        coord_array[1] = item.address.location.coordinates[0]
        var marker = L.marker(coord_array, {icon: greenIcon}).addTo(markerResultsFilterGroup).on('click', function(e) {            
            placeholder_description.empty()
            let html = '';
            html += `<b>Description:</b> + ${item.description}`
            placeholder_description.append(html)
        });
        marker.bindPopup("<b>Street:</b>"+item.address.street +"<br/><b>Name:</b>" + item.name +'<br/><b>Score:</b>' + item.score +"<br/><b>Property Type:</b>" + item.property_type).openPopup()
    });
}