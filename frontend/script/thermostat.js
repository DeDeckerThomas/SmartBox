const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint = '/api/v1/';

let DOMTemperature, DOMHumidity;

const showHumidity = function (jsonObject) {
  console.log(jsonObject);
  DOMHumidity.innerHTML = jsonObject.Value;
};

const showTemperature = function (jsonObject) {
  console.log(jsonObject);
  DOMTemperature.innerHTML = jsonObject.Value;
};

const showGraphHumidity = function (jsonObject) {
  labels = [];
  data = [];
  for (const measurement of jsonObject.reverse()) {
    labels.push(new Date(measurement.Date).toLocaleDateString());
    data.push(measurement.Value);
  }
  console.log(labels);
  var chart = new Chartist.Line(
    '.ct-humidity',
    {
      labels: labels,
      series: [data],
    },
    {
      low: 0,
      high: 100,
      showArea: true,
      showPoint: false,
      height: '450px',
    }
  );

  chart.on('draw', function (data) {
    if (data.type === 'line' || data.type === 'area') {
      data.element.animate({
        d: {
          begin: 2000 * data.index,
          dur: 2000,
          from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
          to: data.path.clone().stringify(),
          easing: Chartist.Svg.Easing.easeOutQuint,
        },
      });
    }
  });
};

const showGraphTemperature = function (jsonObject) {
  labels = [];
  data = [];
  for (const measurement of jsonObject.reverse()) {
    labels.push(new Date(measurement.Date).toLocaleDateString());
    data.push(measurement.Value);
  }
  var chart = new Chartist.Line(
    '.ct-temperature',
    {
      labels: labels,
      series: [data],
    },
    {
      low: 10,
      high: 30,
      showArea: true,
      showPoint: false,
      height: '450px',
    }
  );

  chart.on('draw', function (data) {
    if (data.type === 'line' || data.type === 'area') {
      data.element.animate({
        d: {
          begin: 2000 * data.index,
          dur: 2000,
          from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
          to: data.path.clone().stringify(),
          easing: Chartist.Svg.Easing.easeOutQuint,
        },
      });
    }
  });
};

const getHistoryHumidity = function () {
  handleData(`http://${lanIP}${endpoint}sensors/2/history/`, showGraphHumidity);
};

const getHistoryTemperature = function () {
  handleData(`http://${lanIP}${endpoint}sensors/1/history/`, showGraphTemperature);
};

const init = function () {
  DOMTemperature = document.querySelector('.js-temperature');
  DOMHumidity = document.querySelector('.js-humidity');
  getHistoryTemperature();
  getHistoryHumidity();
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
