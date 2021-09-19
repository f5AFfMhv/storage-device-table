/* Page reload by setting slider */

var slider = document.getElementById("setSlider");
var setTime = document.getElementById("sliderValue");
var checkbox = document.getElementById("enableTimer");
var leftTime = document.getElementById("leftTime");
var progress = document.getElementById("progressCountdown");
var sliderRow = document.getElementById("sliderRow");
var progressRow = document.getElementById("progressRow");

// Try to get slider and checkbox values from local storage
var savedInterval = localStorage.getItem("interval");
var savedCheckbox = localStorage.getItem("checkbox");

// If slider value is in local store assign it again to slider
if (savedInterval !== null) {
  slider.value = savedInterval;
}

// Display initial reload time on webpage
setTime.innerHTML = slider.value + " min";
progressRow.style.display = "none";

// On slider input update displayed reload time
slider.oninput = function() {
setTime.innerHTML = this.value + " min";
}

// Function for converting seconds to min:sec
function secondsConvert(sec) {
  var minutes = Math.floor(sec / 60);
  var seconds = (sec % 60).toFixed(0);
  return minutes + " min " + (seconds < 10 ? '0' : '') + seconds + " s";
}

// Function for counting down
function countDown() {
  if (timeleft > 1) {
    // Update page with new values
    timeleft--;
    progress.value = timeleft;
    leftTime.innerHTML = secondsConvert(timeleft);
  } else {
    // If countdown reached 0, reload page
    location.reload();
  }
}

// Function for setting parameters after page reload when checkbox checked value was found on local storage to be true
function afterReload() {
  // Set and display values from local store
  timeleft = slider.value * 60;
  progress.value = timeleft;
  progress.max = timeleft;
  leftTime.innerHTML = secondsConvert(progress.value);
  // Disable range slider
  slider.disabled = true; 
  sliderRow.style.display = "none";
  // Show progress bar
  progressRow.style.display = "block";
  // Start 1s timer
  window.reloadIntervalId = setInterval(countDown, 1000);
}

// Function to execute when interacting with checkbox
checkbox.onclick = function() {
  // Save current range slider and checkbox values to local storage
  localStorage.setItem("interval", slider.value);
  localStorage.setItem("checkbox", checkbox.checked);
  if (this.checked) {
    // Set and display values from input objects
    timeleft = slider.value * 60;
    progress.value = timeleft;
    progress.max = timeleft;
    leftTime.innerHTML = secondsConvert(progress.value);
    // Disable range slider
    slider.disabled = true; 
    sliderRow.style.display = "none";
    // Show progress bar
    progressRow.style.display = "block";
    // Start 1s timer
    window.reloadIntervalId = setInterval(countDown, 1000);
    // If checkbox is unchecked
  } else {
    leftTime.innerHTML = "";
    // Show range slider
    slider.disabled = false;
    sliderRow.style.display = "block";
    // Hide progress bar
    progressRow.style.display = "none";
    // Stop timer
    clearInterval(reloadIntervalId);
  }   
}

// If checkbox checked value exists in local storage and is true, call afterReload function
if (savedCheckbox == "true") {
  checkbox.checked = true;
  afterReload();
} else {
  checkbox.checked = false;
}