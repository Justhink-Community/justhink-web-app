const secondaryLanguageSelection = document.querySelector(
    ".language-selection--secondary"
  ),
  languageSwitch = document.querySelector(".language-switch"),
  loginBox = document.querySelector(".login-box"),
  loginContainer = document.querySelector(".login-container"),
  registerContainer = document.querySelector(".register-container"),
  publishIdeaLink = document.querySelector(".publish-idea"),
  publishIdeaBox = document.querySelector(".publish-idea-box"),
  publishIdeaContainer = document.querySelector(".publish-idea-container"),
  informationBox = document.querySelector('.information-box')

secondaryLanguageSelection.addEventListener("mouseover", () => {
  languageSwitch.style.backgroundColor = "#e4e4e4";
});

secondaryLanguageSelection.addEventListener("mouseout", () => {
  languageSwitch.style.backgroundColor = "#ebebeb";
});

document.querySelector("html").addEventListener("click", (e) => {



  if (
    !loginBox.contains(e.target) &&
    loginBox.classList.contains("showed") &&
    e.target != document.querySelector(".btn")
  ) {
    loginBox.classList.remove("showed");
  } else if (
    !publishIdeaContainer.contains(e.target) &&
    e.target != document.querySelector(".publish-idea svg") && publishIdeaBox.classList.contains('writing-idea')
  ) {
    publishIdeaBox.classList.remove("writing-idea");
    publishIdeaBox.classList.add("inspecting-ideas");
  }


});

const logInSimulate = () => {
  loginBox.classList.toggle("showed");
  registerContainer.classList.remove("active");
  loginBox.classList.contains("showed")
    ? loginContainer.classList.add("active")
    : false;
};

const simulateAuthModeChange = () => {
  if (loginContainer.classList.contains("active")) {
    loginContainer.classList.remove("active");
    registerContainer.classList.add("active");
  } else {
    loginContainer.classList.add("active");
    registerContainer.classList.remove("active");
  }
};

publishIdeaLink.addEventListener('click', () => {
  // console.log('hi')
  let linkIcon = publishIdeaLink.querySelector("svg");
  if (linkIcon.classList.contains('add')) {
    publishIdeaBox.classList.add("writing-idea");
    publishIdeaBox.classList.remove("inspecting-ideas");
  } 
})

// IDEAS 

const ideas = document.querySelectorAll('.idea');

ideas.forEach(idea => {
  idea.addEventListener('click', (e) => {
    if (! (idea.querySelector('menu').contains(e.target)) ) {

      window.location.replace(idea.querySelector('.idea__comment-btn').getAttribute('href'))
    }
  })
});

