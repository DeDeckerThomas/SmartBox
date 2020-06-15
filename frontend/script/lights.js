const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let domDevices;

const listenToSwitches = function () {
  let switches = document.querySelectorAll('.js-switch');
  for (let i = 0; i < switches.length; i++) {
    switches[i].addEventListener('input', () => {
      let body = JSON.stringify({
        status: switches[i].checked,
        isactive: switches[i].checked ? 1 : 0,
      });
      console.log(body);
      updateDevice(switches[i].id, body);
    });
  }
};

const listenToLights = function () {
  let devices = document.querySelectorAll('.js-device');
  for (const device of devices) {
    device.addEventListener('click', () => {
      window.location.href = 'ledstrip.html';
    });
  }
};

const showDevices = function (jsonObject) {
  html = ``;
  for (let device of jsonObject) {
    html += `
      <div class="c-alarm">
        <div class="o-layout o-layout--align-end js-device">
          <p class="c-lead c-lead-md u-mb-clear">${device.Name}</p>
        </div>
        <label class="c-switch" for="${device.DeviceID}">
          <input class="c-switch__label js-switch" type="checkbox" ${device.IsActive == 1 ? 'checked' : ''}  name="${device.Name}" id="${device.DeviceID}" />
          <span class="c-switch__slider"></span>
        </label>
      </div>
    `;
  }
  domDevices.innerHTML = html;
  listenToLights();
  listenToSwitches();
};

const test = function () {
  console.log('test');
};

const updateDevice = function (id, body) {
  handleData(`http://${lanIP}${endpoint}users/1/devices/${id}/update`, test, (method = 'PUT'), (body = body));
};

const getDevices = function () {
  handleData(`http://${lanIP}${endpoint}users/1/devices/`, showDevices);
};

const init = function () {
  domDevices = document.querySelector('.js-devices');
  getDevices();
};

document.addEventListener('DOMContentLoaded', init);
