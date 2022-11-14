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
    e.target != document.querySelector(".publish-idea ion-icon") && publishIdeaBox.classList.contains('writing-idea')
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
  let linkIcon = publishIdeaLink.querySelector("ion-icon");
  if (linkIcon.getAttribute("name") == "add-outline") {
    publishIdeaBox.classList.add("writing-idea");
    publishIdeaBox.classList.remove("inspecting-ideas");
  } 
})

// AJAX 

const publishIdeaForm = document.querySelector('.publish-idea-form'),
publishIdeaContent = document.querySelector('.publish-idea__textarea'),
csrf = document.querySelectorAll('.csrfmiddlewaretoken')


publishIdeaForm.addEventListener('submit', e => {
  e.preventDefault() 

  const formData = new FormData()
  formData.append('csrfmiddlewaretoken', csrf[0].value)
  formData.append('idea-content', publishIdeaContent.value)

  $.ajax({
    type: 'POST',
    url: '',
    enctype: 'multipart/form-data',
    data: formData,
    success: function(response)  {
      console.log(response)
    },
    error: function(err) {
      console.log(err)
    },
    cache: false,
    contentType: false, 
    processData: false
  })

})