const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
let selectedDays = [];

let domSave, domDays, domBack, domName, domStartime, domDuration;

const listenToDeleteButton = function (alarmid) {
  let domDelete = document.querySelector('.js-delete');
  domDelete.addEventListener('click', () => {
    deleteAlarm(alarmid);
  });
};

const addDeleteButton = function (alarmid) {
  let domButtons = document.querySelector('.js-buttons');
  domButtons.innerHTML += `<a class="o-button-reset c-button js-delete">Delete</a>`;
  listenToDeleteButton(alarmid);
};

function arrayRemove(arr, value) {
  return arr.filter(function (ele) {
    return ele !== value;
  });
}

const listenToSave = function () {
  let domSave = document.querySelector('.js-save');
  domSave.addEventListener('click', () => {
    let body = JSON.stringify({
      name: domName.value,
      starttime: domStartime.value,
      duration: domDuration.value,
      days: selectedDays,
    });
    let alarmid = getQueryParams('alarmid', window.location.href);
    if (alarmid) {
      putAlarm(alarmid, body);
    } else {
      postAlarm(body);
    }
  });
};

const listenToDays = function () {
  let listenDays = document.querySelectorAll('.js-day');
  for (let day of listenDays) {
    day.addEventListener('click', () => {
      if (day.classList.contains('c-day--active')) {
        day.classList.remove('c-day--active');
        selectedDays = arrayRemove(selectedDays, day.dataset.day);
      } else {
        day.classList.add('c-day--active');
        selectedDays.push(day.dataset.day);
      }
      console.log(selectedDays);
    });
  }
};

const listenToBackButton = function () {
  domBack.addEventListener('click', () => {
    window.history.back();
  });
};

const getQueryParams = (params, url) => {
  let href = url;
  let reg = new RegExp('[?&]' + params + '=([^&#]*)', 'i');
  let queryString = reg.exec(href);
  return queryString ? queryString[1] : null;
};

const showAlarm = function (jsonObject) {
  console.log(jsonObject);
  domName.value = jsonObject.Name;
  domStartime.value = jsonObject.StartTime;
  domDuration.value = jsonObject.Duration;
  let html = '';

  for (let day of days) {
    if (jsonObject.Days.includes(day)) selectedDays.push(day);
    html += `
      <a class="c-day ${jsonObject.Days.includes(day) ? 'c-day--active' : ''} js-day" data-day="${day}">
        <p class="c-lead c-lead--day u-color--white u-mb-clear">${day.substring(0, 3)}</p>
      </a>
      `;
  }
  domDays.innerHTML = html;
  listenToDays();
};

const deleteAlarm = function (alarmid) {
  handleData(
    `http://${lanIP}${endpoint}users/1/alarms/${alarmid}`,
    () => {
      window.history.back();
    },
    'DElETE'
  );
};

const putAlarm = function (alarmid, body) {
  handleData(`http://${lanIP}${endpoint}users/1/alarms/${alarmid}`, getAlarm, 'PUT', body);
};

const postAlarm = function (body) {
  handleData(`http://${lanIP}${endpoint}users/1/alarms/`, getAlarm, 'POST', body);
};

const getAlarm = function (alarmid) {
  handleData(`http://${lanIP}${endpoint}users/1/alarms/${alarmid}`, showAlarm);
};

const init = function () {
  domName = document.querySelector('.js-name');
  domStartime = document.querySelector('.js-starttime');
  domDuration = document.querySelector('.js-duration');
  domDays = document.querySelector('.js-days');
  domBack = document.querySelector('.js-back');
  listenToBackButton();
  listenToDays();
  let alarmid = getQueryParams('alarmid', window.location.href);
  if (alarmid) {
    getAlarm(alarmid);
    addDeleteButton(alarmid);
  }
  listenToSave();
};

document.addEventListener('DOMContentLoaded', init);
