"use strict";

var fs = require('fs');
var path = require('path');
var R = require('ramda');
var Immutable = require('immutable');

var testDataDir = path.join('..', 'test_data');
// var fileName = path.join('..', 'test_data', 'elizabeth_cotton.txt');
var hostnameRegex = /(\S+)\#sh[ow\s]+ver.*/;
var serialNumberRegex = /[Ss]ystem\s+[Ss]erial\s+[Nn]umber\s+:\s([\w]+)/g;
var modelSoftwareRegex = /([\w-]+)\s+(\d{2}\.[\w\.)?(?]+)\s+(\w+[-|_][\w-]+\-[\w]+)/g;


function parseFile(fileName) {
  fileName = path.join(testDataDir, fileName);
  var fileContent = fs.readFileSync(fileName, 'utf8');

  // Get hostname
  var hostname = hostnameRegex.exec(fileContent)[1];

  // Get Serial Numbers
  var serialNumberArray = [];
  var serialNumberMatch;

  while (serialNumberMatch = serialNumberRegex.exec(fileContent)) {
    serialNumberArray.push(serialNumberMatch[1]);
  };

  // Get Model, Software Version & Software Image
  var modelNumberArray = [];
  var softwareVersionArray = [];
  var softwareImageArray = [];
  var modelSoftwareMatch;

  while (modelSoftwareMatch = modelSoftwareRegex.exec(fileContent)) {
    // console.log(modelSoftwareMatch);
    modelNumberArray.push(modelSoftwareMatch[1]);
    softwareVersionArray.push(modelSoftwareMatch[2]);
    softwareImageArray.push(modelSoftwareMatch[3]);
  };

  var device = Immutable.Map(
    {
      hostname:hostname,
      serialNumbers:serialNumberArray,
      modelNumbers:modelNumberArray,
      softwareVersions:softwareVersionArray,
      softwareImages:softwareImageArray
    });

  console.log(device);

  /*
  console.log('\n')
  console.log("Hostname: " + hostname);
  console.log("Serial Numbers: " + serialNumberArray);
  console.log("Model Numbers: " + modelNumberArray);
  console.log("Software Versions: " + softwareVersionArray);
  console.log("Software Images: " + softwareImageArray);
  */

}



// Loop through test Data directory
fs.readdir(testDataDir, function(err, files) {
  R.map(parseFile, files)
});
