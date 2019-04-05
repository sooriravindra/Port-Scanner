let applicationSession = null;

const startScan = scanRequestParams => {
  // Hide form and show spinner
  $(".formdiv").hide();
  $(".spinner").show();
  applicationSession.publish("scan.start", [scanRequestParams]);
};

$(document).ready(() => {
  $("#scan_request").submit(function(event) {
    //pack it as a dictionary before sending
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
  $(".spinner").hide();
  $(".results").show();

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

const ROUTER_ENDPOINT = "ws://"+location.host+"/ws";
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
