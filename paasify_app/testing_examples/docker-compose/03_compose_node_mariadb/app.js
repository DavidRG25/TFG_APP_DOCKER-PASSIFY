var http = require('http');
var os = require('os');

var server = http.createServer(function (request, response) {
  response.writeHead(200, {"Content-Type": "application/json"});
  response.end(JSON.stringify({
      "message": "Hello from Node.js with MariaDB",
      "hostname": os.hostname(),
      "platform": os.platform()
  }));
});

server.listen(3000);
console.log("Server running at http://0.0.0.0:3000/");
