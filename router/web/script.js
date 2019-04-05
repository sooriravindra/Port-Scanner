function sleep(time) {
  console.log("Inside sleep");
  return new Promise(resolve => setTimeout(resolve, time));
}

var applicationSession = null;

function onScan() {
  console.log("Inside onScan");

  // Hide form and show spinner
  $(".formdiv").hide();
  $(".spinner").show();

  applicationSession.publish("scan.start");

  // Display results table after 4s for now
  sleep(4000).then(() => {
    console.log("Resolved sleep");
    $(".spinner").hide();
    $(".results").show();
  });

  // Return false to prevent form submission
  return false;
}

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
};

connection.open();
