const ipcRenderer = require('electron').ipcRenderer;
const remote = require('electron').remote;
const dialog = remote.require('dialog');

var showFilesDirButton = document.getElementById('showFilesDirSelect');

showFilesDirButton.addEventListener('click', function (event) {
  var showFilesDir = dialog.showOpenDialog({ properties: ['openDirectory'] });
  document.getElementById('showFilesDirPath').value = showFilesDir;
    //ipcRenderer.send('build', showFilesDir);
})

var buildButton = document.getElementById('build');

buildButton.addEventListener('click', function (event) {
  var showFilesDirPath = document.getElementById('showFilesDirPath').value;
  ipcRenderer.send('build', showFilesDirPath);
});

//ipcRenderer.on('result', function (event, arg) {
//    console.log(arg);
//});