var map;
function initMap() {
  map = new google.maps.Map(document.getElementById('map_canvas'), {
    center: {lat: 35.681, lng: 139.766},
    zoom: 5
  });
  setMarker();
}

function setMarker() {
  var url_base = "https://maps.googleapis.com/maps/api/geocode/json?address="
  var url_key = "&key=AIzaSyB3pOq5XcaOp-IpKZKwKZ0K333ylKtcTM8"
  var addresses = document.querySelectorAll("#result_from_url li")

  addresses.forEach(function(address) {
    var url_address = address.innerHTML;
    var url = url_base + url_address + url_key;
    var request = new XMLHttpRequest();
    request.open('GET', url);
    request.send();
    request.onreadystatechange = function () {
      if (request.readyState === 4 && request.status === 200) {
        var res = JSON.parse(request.responseText);
        var lat = res["results"][0]["geometry"]["location"]["lat"]
        var lng = res["results"][0]["geometry"]["location"]["lng"]
        var marker = new google.maps.Marker({
          position: {lat: lat, lng: lng}
        });
        marker.setMap(map);
      }
    };

  });
}
