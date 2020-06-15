const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let domShutdown, domMinTemp, domMaxTemp, domMinHum, domMaxHum, domSave;

const listenToShutdown = function () {
  domShutdown.addEventListener('click', () => {
    shutdownPi();
  });
};

const listenToSave = function () {
  domSave.addEventListener('click', function () {
    let body = JSON.stringify({
      userid: 1,
      mintemp: document.querySelector('.js-mintemp').value,
      maxtemp: document.querySelector('.js-maxtemp').value,
      minhum: document.querySelector('.js-minhum').value,
      maxhum: document.querySelector('.js-maxhum').value,
    });
    putSettings(body);
  });
};

const showSettings = function (jsonObject) {
  domMinTemp.value = jsonObject.MinTemp;
  domMaxTemp.value = jsonObject.MaxTemp;
  domMinHum.value = jsonObject.MinHum;
  domMaxHum.value = jsonObject.MaxHum;
};

const shutdownPi = function () {
  handleData(`http://${lanIP}${endpoint}poweroffpi/`, (jsonObject) => {
    console.log(jsonObject);
  });
};

const putSettings = function (body) {
  handleData(`http://${lanIP}${endpoint}users/1/settings/`, getSettings, 'PUT', body);
};

const getSettings = function () {
  handleData(`http://${lanIP}${endpoint}users/1/settings/`, showSettings);
};

const init = function () {
  domMinTemp = document.querySelector('.js-mintemp');
  domMaxTemp = document.querySelector('.js-maxtemp');
  domMinHum = document.querySelector('.js-minhum');
  domMaxHum = document.querySelector('.js-maxhum');
  domSave = document.querySelector('.js-save');
  domShutdown = document.querySelector('.js-shutdown');
  listenToSave();
  listenToShutdown();
  getSettings();
};

document.addEventListener('DOMContentLoaded', init);
