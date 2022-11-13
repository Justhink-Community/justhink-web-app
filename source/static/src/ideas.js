
const countdownValue = document.querySelector('.countdown__value'),
controllerStart = document.querySelector('.controller__start')
let COUNTDOWN_STOPPED = false 

function startCountdown() {
  countdownValue.innerHTML = 90
  setInterval(() => {
    if (!COUNTDOWN_STOPPED) {
      countdownValue.innerHTML -= 1

      if (countdownValue.innerHTML == 0) {
        window.location.reload()
      }
    }
  }, 1000)
}

function stopCountdown() {
  COUNTDOWN_STOPPED = !COUNTDOWN_STOPPED;
  COUNTDOWN_STOPPED == true ? controllerStart.innerHTML = 'play_circle': controllerStart.innerHTML = 'pause_circle'
} 

startCountdown()