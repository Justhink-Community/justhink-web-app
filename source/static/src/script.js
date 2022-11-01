const secondaryLanguageSelection = document.querySelector('.language-selection--secondary'),
languageSwitch = document.querySelector('.language-switch')

secondaryLanguageSelection.addEventListener('mouseover', () => {
  languageSwitch.style.backgroundColor = '#e4e4e4'
});

secondaryLanguageSelection.addEventListener('mouseout', () => {
  languageSwitch.style.backgroundColor = '#ebebeb'
});