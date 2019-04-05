function sleep(time) {
  console.log("Inside sleep");
  return new Promise(resolve => setTimeout(resolve, time));
}

var applicationSession = null;

const startScan = scanRequestParams => {
  // Hide form and show spinner
  $(".formdiv").hide();
  $(".spinner").show();

  applicationSession.publish("scan.start", [scanRequestParams]);

  // Display results table after 4s for now
  sleep(1000).then(() => {
    console.log("Resolved sleep");
    $(".spinner").hide();
    $(".results").show();
  });
};

$(document).ready(() => {
  $("#scan_request").submit(function(event) {
    //pack it as a single argument
    const scanRequestParams = $(this)
      .serializeArray()
      .reduce((scanRequestParams, param) => {
        scanRequestParams[param["name"]] = param["value"];
        return scanRequestParams;
      }, {});

    startScan(scanRequestParams);
    event.preventDefault();
  });
});

const scanResult = status => {
  const ip = status[0]["ip"];
  const port = status[0]["port"];
  const scanStatus = parseInt(status[0]["status"]);
  const results = $("#scan-results");
  const length = results.length;

  const row = $("<tr/>");
  const idCell = $("<td/>");
  const ipCell = $("<td/>");
  const portCell = $("<td/>");
  const scanStatusCell = $("<td/>");

  idCell.append(length);
  ipCell.append(ip);
  portCell.append(port);
  scanStatusCell.append(scanStatus == 1 ? "Alive" : "Not Alive");

  row.append(idCell);
  row.append(ipCell);
  row.append(portCell);
  row.append(scanStatusCell);

  results.append(row);
};

const ROUTER_ENDPOINT = "ws://127.0.0.1:80/ws";
const APPLICATION_REALM = "realm1";

const url = ROUTER_ENDPOINT;
const realm = APPLICATION_REALM;

const connection = new autobahn.Connection({
  url,
  realm
});

connection.onopen = session => {
  applicationSession = session;
  session.subscribe("scan.result", scanResult);
};

connection.open();
