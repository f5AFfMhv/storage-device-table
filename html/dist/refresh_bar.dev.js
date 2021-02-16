"use strict";

ProgressCountdown(60, 'pageBeginCountdown');

function ProgressCountdown(timeleft, bar) {
  return new Promise(function (resolve, reject) {
    var countdownTimer = setInterval(function () {
      timeleft--;
      document.getElementById(bar).value = timeleft;

      if (timeleft <= 0) {
        clearInterval(countdownTimer);
        resolve(true);
        location.reload(true);
      }
    }, 1000);
  });
}