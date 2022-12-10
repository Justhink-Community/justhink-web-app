// const secondaryLanguageSelection = document.querySelector(
//     ".language-selection--secondary"
//   ),
//   languageSwitch = document.querySelector(".language-switch"),
const
  publishIdeaLink = document.querySelector(".publish-idea"),
  publishIdeaBox = document.querySelector(".publish-idea-box"),
  publishIdeaContainer = document.querySelector(".publish-idea-container"),
  informationBox = document.querySelector(".information-box"),
  myAccount = document.querySelector(".my-account");

// secondaryLanguageSelection.addEventListener("mouseover", () => {
//   languageSwitch.style.backgroundColor = "#e4e4e4";
// });

// secondaryLanguageSelection.addEventListener("mouseout", () => {
//   languageSwitch.style.backgroundColor = "#ebebeb";
// });

document.querySelector("html").addEventListener("click", (e) => {
 if (
    !publishIdeaContainer.contains(e.target) &&
    e.target != document.querySelector(".publish-idea svg") &&
    publishIdeaBox.classList.contains("writing-idea")
  ) {
    publishIdeaBox.classList.remove("writing-idea");
    publishIdeaBox.classList.add("inspecting-ideas");
  } else if (
    !myAccount.contains(e.target) &&
    myAccount.classList.contains("showed") &&
    e.target != document.querySelector(".btn")
  ) {
    myAccount.classList.remove("showed");
  }
});

try {
  publishIdeaLink.addEventListener("click", () => {
    // console.log('hi')
    let linkIcon = publishIdeaLink.querySelector("svg");
    if (linkIcon.classList.contains("add")) {
      publishIdeaBox.classList.add("writing-idea");
      publishIdeaBox.classList.remove("inspecting-ideas");
    }
  });
} catch (error) {
  
}

// IDEAS

const ideas = document.querySelectorAll(".idea");

ideas.forEach((idea) => {
  idea.addEventListener("click", (e) => {
    console.log(
      !idea.querySelector(".idea__interaction-btns").contains(e.target)
    );
    if (
      !idea.querySelector(".idea__interaction-btns").contains(e.target) &&
      e.target.tagName == "a"
    ) {
      window.location.replace(
        idea.querySelector(".idea__comment-btn").getAttribute("href")
      );
    }
  });
});

// PROFILE

const expandMyAccount = () => {
  myAccount.classList.toggle("showed");
};

// VPN 


