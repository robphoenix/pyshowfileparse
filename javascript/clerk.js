'use strict';

var fs = require('fs');
var path = require('path');
var R = require('ramda');
var Immutable = require('immutable');

var testDataDir = 'C:\\Users\\robertph\\RobBT\\RepeatableDesign\\python_scripts\\inventory_generation\\alexey-show-files' // path.join('..', 'test_data');
var hostnameRegex = /(\S+)\#sh[ow\s]+ver.*/;
var serialNumberRegex = /[Ss]ystem\s+[Ss]erial\s+[Nn]umber\s+:\s([\w]+)/g;
var modelSoftwareRegex = /([\w-]+)\s+(\d{2}\.[\w\.)?(?]+)\s+(\w+[-|_][\w-]+\-[\w]+)/g;


function fetchHostname(fileContent) {
  return hostnameRegex.exec(fileContent)[1];
};

function fetchSerialNumbers(fileContent) {
  var serialNumberArray = [];
  var serialNumberMatch;

  while (serialNumberMatch = serialNumberRegex.exec(fileContent)) {
    serialNumberArray.push(serialNumberMatch[1]);
  };

  return serialNumberArray;
};

function fetchModelAndSoftware(fileContent) {
  var allModelSoftwareArray = [];
  var modelSoftwareMatch;

  while (modelSoftwareMatch = modelSoftwareRegex.exec(fileContent)) {
    var eachModelSoftwareArray = [];
    eachModelSoftwareArray.push(modelSoftwareMatch[1]);
    eachModelSoftwareArray.push(modelSoftwareMatch[2]);
    eachModelSoftwareArray.push(modelSoftwareMatch[3]);
    allModelSoftwareArray.push(eachModelSoftwareArray);
  };

  return allModelSoftwareArray;
}

function parseFile(fileName) {
  fileName = path.join(testDataDir, fileName);
  var fileContent = fs.readFileSync(fileName, 'utf8');

  var hostname = fetchHostname(fileContent);
  var serialNumbers = fetchSerialNumbers(fileContent);
  var modelAndSoftware = fetchModelAndSoftware(fileContent);

  var deviceList = [];

  var i = 0;
  while (i < serialNumbers.length) {
    var device = Immutable.List([
      hostname,
      serialNumbers[i],
      modelAndSoftware[i][0],
      modelAndSoftware[i][1],
      modelAndSoftware[i][2]
    ]);

    deviceList.push(device.join());
    i++;
  }

  return deviceList;
}

// Loop through test Data directory
function buildData(dir) {
  var output = "Hostname,Serial Number,Model,Software Version,Software Image\n";
  fs.readdirSync(dir).map(function(file) {
    parseFile(file).map(function(device) {
      output += device;
      output += "\n"
    });
  });
  return output;
}

function writeDataToCSV(content) {
  var d = new Date()
  var filename = "Inventory-" + d.getFullYear() + "-" + (d.getMonth() +1) + "-" + d.getDate() + "-" + d.getHours() + d.getMinutes() + d.getSeconds() + ".csv"
  fs.writeFileSync(filename, content);
}

console.log(buildData(testDataDir));
writeDataToCSV(buildData(testDataDir));
