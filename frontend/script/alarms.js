const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let domAdd, domAlarms;

const listenToAddButton = function () {
  domAdd.addEventListener('click', () => {
    window.location.href = `alarm.html`;
  });
};

const listenToAlarms = function () {
  let alarms = document.querySelectorAll('.js-alarm');
  let values = document.querySelectorAll('.js-alarm-value');
  console.log(values);
  for (let i = 0; i < alarms.length; i++) {
    alarms[i].addEventListener('click', () => {
      console.log(values[i]);
      window.location.href = `alarm.html?alarmid=${values[i].id}`;
    });
  }
};

const listenToSwitches = function () {
  let switches = document.querySelectorAll('.js-switch');
  for (let i = 0; i < switches.length; i++) {
    switches[i].addEventListener('input', () => {
      let body = JSON.stringify({
        status: switches[i].checked,
      });
      updateAlarm(switches[i].id, body);
    });
  }
};

const formatTime = function (time) {
  let result = time.split(':');
  return `${result[0]}:${result[1]}`;
};

const showAlarms = function (jsonObject) {
  let html = '';
  for (const alarm of jsonObject) {
    html += `
    <div class="c-alarm">
        <div class="o-layout o-layout--align-end  js-alarm">
        <div class="u-mr-lg">
            <p class="c-lead c-lead-md u-mb-clear">${alarm.Name}</p>
            <p class="c-lead c-lead--xxl u-mb-clear">${formatTime(alarm.StartTime)}</p>
        </div>
        <p class="c-lead c-lead-md u-mb-clear">${alarm.Days.map((str) => {
          return str.substring(0, 3);
        }).join(', ')}</p>
        </div>
        <label class="c-switch" for="${alarm.AlarmID}">
        <input class="c-switch__label js-switch js-alarm-value" type="checkbox" ${alarm.IsActive == 1 ? 'checked' : ''} name="${alarm.Name}" id="${alarm.AlarmID}" />
        <span class="c-switch__slider"></span>
        </label>
    </div>
  `;
  }
  domAlarms.innerHTML = html;
  listenToSwitches();
  listenToAlarms();
};

const updateAlarm = function (alarmid, body) {
  handleData(`http://${lanIP}${endpoint}users/1/alarms/${alarmid}/update`, getAlarms, 'PUT', body);
};

const getAlarms = function () {
  handleData(`http://${lanIP}${endpoint}users/1/alarms/`, showAlarms);
};

const init = function () {
  domAlarms = document.querySelector('.js-alarms');
  domAdd = document.querySelector('.js-add');
  listenToAddButton();
  getAlarms();
};

document.addEventListener('DOMContentLoaded', init);
