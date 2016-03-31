const ipcRenderer = require('electron').ipcRenderer;
const remote = require('electron').remote;
const dialog = remote.require('dialog');

var d = new Date()
var defaultFilename = "Inventory-" + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate() + "-" + d.getHours() + d.getMinutes() + d.getSeconds();
document.getElementById('inventoryFilename').value = defaultFilename;

var showFilesDirButton = document.getElementById('showFilesDirSelect');
var outputDirButton = document.getElementById('outputDirSelect');

showFilesDirButton.addEventListener('click', function (event) {
  var showFilesDir = dialog.showOpenDialog({ properties: ['openDirectory'] });
  document.getElementById('showFilesDirPath').value = showFilesDir;
  //ipcRenderer.send('build', showFilesDir);
});

outputDirButton.addEventListener('click', function (event) {
  var outputDir = dialog.showOpenDialog({ properties: ['openDirectory'] });
  document.getElementById('outputDirPath').value = outputDir;
    //ipcRenderer.send('build', showFilesDir);
})

var buildButton = document.getElementById('build');

buildButton.addEventListener('click', function (event) {
  var showFilesDirPath = document.getElementById('showFilesDirPath').value;
  var outputDirPath = document.getElementById('outputDirPath').value;
  var inventoryFilename = document.getElementById('inventoryFilename').value;
  ipcRenderer.send('build', showFilesDirPath, outputDirPath, inventoryFilename);
});

//ipcRenderer.on('result', function (event, arg) {
//    console.log(arg);
//});