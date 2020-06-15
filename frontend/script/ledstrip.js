const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let domBack, domSave, domName, domType, domColor, domPattern;

const listenToBackButton = function () {
  domBack.addEventListener('click', () => {
    window.history.back();
  });
};

const listenToSave = function () {
  domSave.addEventListener('click', function () {
    let body = JSON.stringify({
      type: domType.value,
      color: domType.value === 'color' ? document.querySelector('#color').value : 'null',
      pattern: domType.value === 'pattern' ? document.querySelector('#pattern').value : 'None',
    });
    console.log(body);
    putDevice(body);
  });
};

const listenToType = function () {
  domType.addEventListener('input', () => {
    let selectedValue = domType.options[domType.selectedIndex].value;
    if (selectedValue === 'color') {
      domPattern.classList.add('u-hide');
      domColor.classList.remove('u-hide');
    } else if (selectedValue == 'pattern') {
      domPattern.classList.remove('u-hide');
      domColor.classList.add('u-hide');
    }
  });
};

const showDevice = function (jsonObject) {
  console.log(jsonObject);
  domName.value = jsonObject.Name;
  domType.value = jsonObject.Color == 'null' ? 'pattern' : 'color';
  if (domType.value === 'color') {
    domPattern.classList.add('u-hide');
    domColor.classList.remove('u-hide');
    document.querySelector('#color').value = jsonObject.Color;
  } else if (domType.value == 'pattern') {
    domPattern.classList.remove('u-hide');
    domColor.classList.add('u-hide');
    document.querySelector('#pattern').value = jsonObject.Pattern;
  }
};

const putDevice = function (body) {
  handleData(`http://${lanIP}${endpoint}users/1/devices/1`, getDevice, 'PUT', body);
};

const getDevice = function () {
  handleData(`http://${lanIP}${endpoint}users/1/devices/1`, showDevice);
};

const init = function () {
  domName = document.querySelector('.js-name');
  domType = document.querySelector('.js-type');
  domColor = document.querySelector('.js-color');
  domPattern = document.querySelector('.js-pattern');
  domSave = document.querySelector('.js-save');
  domBack = document.querySelector('.js-back');
  listenToSave();
  listenToBackButton();
  getDevice();
  listenToType();
};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  init();
});
