// script.js
document.addEventListener("DOMContentLoaded", () => {
    // Add your event listeners or interactive functionality here
    console.log("The Grey Canvas website is ready!");
});

// in js/script.js:
window.addEventListener('scroll', () => {
  const header = document.querySelector('header');
  if (window.scrollY > 50) {
      header.classList.add('scrolled');
  } else {
      header.classList.remove('scrolled');
  }
});
