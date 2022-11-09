const secondaryLanguageSelection = document.querySelector(
    ".language-selection--secondary"
  ),
  languageSwitch = document.querySelector(".language-switch"),
  loginBox = document.querySelector(".login-box"),
  loginContainer = document.querySelector(".login-container"),
  registerContainer = document.querySelector(".register-container"),
  publishIdeaLink = document.querySelector("a.publish-idea"),
  publishIdeaBox = document.querySelector(".publish-idea-box"),
  publishIdeaContainer = document.querySelector(".publish-idea-container");

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
    e.target != document.querySelector("a.publish-idea ion-icon") && publishIdeaBox.classList.contains('writing-idea')
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

const shareIdea = () => {
  let linkIcon = publishIdeaLink.querySelector("ion-icon");
  if (linkIcon.getAttribute("name") == "add-outline") {
    publishIdeaBox.classList.add("writing-idea");
    publishIdeaBox.classList.remove("inspecting-ideas");
  } else {
  }
};
