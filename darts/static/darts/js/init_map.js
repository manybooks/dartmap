var map;
function initMap() {
  map = new google.maps.Map(document.getElementById('map_canvas'), {
    center: {lat: 35.681, lng: 139.766},
    zoom: 8
  });
}
