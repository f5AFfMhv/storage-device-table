//var table_order = ["alert", "warning", "normal"]
const url = "http://192.168.0.2:5000/api/v1/devices/all";

fetch(url).then(data => data.json()).then((json) => {
  var row = "";
  var arr = json;
  for (var i = 0; i < arr.length; i++) {

    var id = arr[i].id;
    var host = arr[i].host;
    var ip = arr[i].ip;
    var device = arr[i].device;
    var state = arr[i].state;
    var used_perc = arr[i].used_perc;
    var updated = arr[i].updated;

    if (arr[i].size_mb >= 104857600) {
      var size = String(Math.round(arr[i].size_mb / 1048576)) + " TB";
    } else if (arr[i].size_mb >= 1048576) {
      var size = String(Math.round(arr[i].size_mb * 10 / 1048576) / 10) + " TB";
    } else if (arr[i].size_mb >= 102400) {
      var size = String(Math.round(arr[i].size_mb / 1024)) + " GB";
    } else if (arr[i].size_mb >= 1024) {
      var size = String(Math.round(arr[i].size_mb * 10 / 1024) / 10) + " GB";
    } else {
      var size = String(arr[i].size_mb) + " MB";
    }

    if (arr[i].free_mb >= 104857600) {
      var free = String(Math.round(arr[i].free_mb / 1048576)) + " TB";
    } else if (arr[i].free_mb >= 1048576) {
      var free = String(Math.round(arr[i].free_mb * 10 / 1048576) / 10) + " TB";
    } else if (arr[i].free_mb >= 102400) {
      var free = String(Math.round(arr[i].free_mb / 1024)) + " GB";
    } else if (arr[i].free_mb >= 1024) {
      var free = String(Math.round(arr[i].free_mb * 10 / 1024) / 10) + " GB";
    } else {
      var free = String(arr[i].free_mb) + " MB";
    }

    if (state == "alert") {
      var color = "red";
    } else if (state == "warning") {
      var color = "yellow";
    } else {
      var color = "lightgreen";
    }

    row += 
      "<td>" + id +
      '</td><td><a href="http://192.168.0.2:5000/graph/' + host + '" target="_blank">' + host + '</a>' +
      "</td><td>" + ip +
      "</td><td>" + device +
      "</td><td>" + state +
      "</td><td>" + size +
      "</td><td>" + free +
      '</td><td align="right">' + used_perc + '% <progress style="width:40px;" value=' + used_perc + ' max="100"></progress>' +
      "</td><td>" + updated +
      '</td><td><a href="http://192.168.0.2:5000/remove/' + id + '"><img alt="DEL" src="img/delete.png" width=20 height=20></a></td>';
    
    var tbody = document.querySelector("#indextable tbody");
    var tr = document.createElement("tr");
    tr.innerHTML = row;
    tr.style.backgroundColor = color;
    tbody.appendChild(tr);
    var row = "";
  }
})