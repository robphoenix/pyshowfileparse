const ipcRenderer = require('electron').ipcRenderer;

var button = document.getElementById('start');

button.addEventListener('click', function (event) {
    ipcRenderer.send('start', 'Started');
});

ipcRenderer.on('result', function (event, arg) {
    console.log(arg);
});