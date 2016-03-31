const ipcRenderer = require('electron').ipcRenderer;
const remote = require('electron').remote;
const dialog = remote.require('dialog');

var showFilesDirButton = document.getElementById('showFilesDir');

showFilesDirButton.addEventListener('click', function (event) {
    var showFilesDir = dialog.showOpenDialog({ properties: ['openDirectory'] });
    console.log(showFilesDir);
    ipcRenderer.send('build', showFilesDir);
})

var buildButton = document.getElementById('build');

buildButton.addEventListener('click', function (event) {
    ipcRenderer.send('build');
});

//ipcRenderer.on('result', function (event, arg) {
//    console.log(arg);
//});