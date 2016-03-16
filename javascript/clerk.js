var fs = require("fs");
var fileName = "\\elizabeth_cotton.txt";
var hostnameRegex = /(\S+)\#sh[ow\s]+ver.*/;

var fileContent = fs.readFileSync(__dirname + fileName, 'utf8');

hostname = hostnameRegex.exec(fileContent)[1];
console.log(hostname);

