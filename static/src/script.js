const secondaryLanguageSelection = document.querySelector('.language-selection--secondary'),
languageSwitch = document.querySelector('.language-switch'),
loginBox = document.querySelector('.login-box')

secondaryLanguageSelection.addEventListener('mouseover', () => {
  languageSwitch.style.backgroundColor = '#e4e4e4'
});

secondaryLanguageSelection.addEventListener('mouseout', () => {
  languageSwitch.style.backgroundColor = '#ebebeb'
}); 

document.querySelector('html').addEventListener('click', (e) => {
  var isClickInsideElement = loginBox.contains(e.target);
  if (!isClickInsideElement && loginBox.classList.contains('showed') && e.target != document.querySelector('.btn')) {
    document.querySelector('.login-box').classList.remove('showed')
  }
})