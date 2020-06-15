//#region ***********  Mobile Navigation ***********
const toggleNavigation = function () {
  const toggleTrigger = document.querySelectorAll('.js-toggle-nav');
  for (let i = 0; i < toggleTrigger.length; i++) {
    toggleTrigger[i].addEventListener('click', function () {
      document.querySelector('body').classList.toggle('has-mobile-nav');
    });
  }
};
//#endregion

document.addEventListener('DOMContentLoaded', toggleNavigation);
