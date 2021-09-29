var map = new L.map('mapid').setView({lon: 0, lat: 0}, 2);
var maxAutoZoom = 15;
var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors' +
        '</a> ',
    tileSize: 256,
});
var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
var googleTer = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
});
var baseMaps = {
    "OpenStreetMap": osmLayer,
    "Google Satellite": googleSat,
    "Google Terrain": googleTer

}
L.control.layers(baseMaps).addTo(map);
osmLayer.addTo(map);
// add a scale at at your map.
var scale = L.control.scale().addTo(map);

// add markers
var markers = L.featureGroup();
markers.addTo(map);

var marker = L.marker([51.5, -0.09], {id: 1}).addTo(map);
toolTip = "<dl>" +
    "<dt>ID: 1</dt>" +
    "<dt>Name: Mikocheni</dt>" +
    "</dl>"
marker.bindTooltip(toolTip);
//marker.bindPopup("<b>Hello world!</b><br><a href=https://github.com/localdevices/libre360#libre360>Link</a>").openPopup();
marker.on("click", function (e) {
    // extract the id of the site from marker
    var id = e.target.options.id
    // construct a relative end point with filtered movies (flt1_0)
    location.href = "https://github.com/localdevices/libre360#libre360"
    //location.href = '/portal/movies/?flt1_0=' + id
});
markers.addLayer(marker);
map.fitBounds(markers.getBounds());
setZoomLevel = Math.min(map.getZoom(), maxAutoZoom);
map.setZoom(setZoomLevel);