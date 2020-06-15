const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let DOMTemperature, DOMHumidity, DOMNotifications, DOMDevices;

const showHumidity = function (jsonObject) {
  console.log(jsonObject);
  DOMHumidity.innerHTML = jsonObject.Value;
};

const showTemperature = function (jsonObject) {
  console.log(jsonObject);
  DOMTemperature.innerHTML = jsonObject.Value;
};

const showNotifications = function (jsonObject) {
  html = ``;
  for (let notification of jsonObject) {
    html += `<div class="c-notification"><p class="c-lead c-lead--md u-color-secondary-dark u-mb-clear">${notification.Description}</p></div>`;
  }
  DOMNotifications.innerHTML = html;
};

const showDevices = function (jsonObject) {
  html = ``;
  for (let device of jsonObject) {
    html += `
    <div class="c-device">
      <div class="o-layout o-layout--align-center">
        <svg class="u-color-white" xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24" viewBox="0 0 24 24" width="24">
          <g><rect fill="none" height="24" width="24" /></g>
          <g>
            <g />
            <path d="M12,3c-0.46,0-0.93,0.04-1.4,0.14C7.84,3.67,5.64,5.9,5.12,8.66c-0.48,2.61,0.48,5.01,2.22,6.56C7.77,15.6,8,16.13,8,16.69 V19c0,1.1,0.9,2,2,2h0.28c0.35,0.6,0.98,1,1.72,1s1.38-0.4,1.72-1H14c1.1,0,2-0.9,2-2v-2.31c0-0.55,0.22-1.09,0.64-1.46 C18.09,13.95,19,12.08,19,10C19,6.13,15.87,3,12,3z M14,19h-4v-1h4V19z M14,17h-4v-1h4V17z M12.5,11.41V14h-1v-2.59L9.67,9.59 l0.71-0.71L12,10.5l1.62-1.62l0.71,0.71L12.5,11.41z" />
          </g>
        </svg>
        <p class="c-lead--md u-color-white u-mb-clear">
          ${device.Name}
        </p>
      </div>
      <p class="c-lead--md u-color-white u-mb-clear">
        ${device.IsActive == 1 ? 'active' : 'inactive'}
      </p>
    </div>
  `;
  }
  DOMDevices.innerHTML = html;
};

const getNotifications = function () {
  handleData(`http://${lanIP}${endpoint}users/1/notifications/`, showNotifications);
};

const getDevices = function () {
  handleData(`http://${lanIP}${endpoint}users/1/devices/`, showDevices);
};

const init = function () {
  DOMTemperature = document.querySelector('.js-temperature');
  DOMHumidity = document.querySelector('.js-humidity');
  DOMNotifications = document.querySelector('.js-notifications');
  DOMDevices = document.querySelector('.js-devices');
  getNotifications();
  getDevices();
  socket.emit('connect');
  socket.on('temperature', function (data) {
    showTemperature(data);
  });
  socket.on('humidity', function (data) {
    showHumidity(data);
  });
};

document.addEventListener('DOMContentLoaded', function () {
  console.info('DOM geladen');
  init();
});
