function sleep(time) {
  console.log("Inside sleep");
  return new Promise(resolve => setTimeout(resolve, time));
}

var applicationSession = null;

const startScan = scanRequestParams => {
  console.log("Inside onScan");

  // Hide form and show spinner
  $(".formdiv").hide();
  $(".spinner").show();

  // dest_ip = dest_ip || "45.33.32.156";
  // dport = dport || 22;
  // mode = mode || "syn_scan";

  applicationSession.publish("scan.start", [scanRequestParams]);

  // Display results table after 4s for now
  sleep(1000).then(() => {
    console.log("Resolved sleep");
    $(".spinner").hide();
    $(".results").show();
  });

  // Return false to prevent form submission
  return false;
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

//
const scanResult = status => {
  console.log(`Scan Result is ${status}`);
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
