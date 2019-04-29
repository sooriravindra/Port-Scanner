$(document).ready(() => {
  $("#scan_request").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".formdiv").hide();
    $(".spinner").show();

    $.post("/submit_task", data).then(status => {
      $(".spinner").hide();
      $(".results").show();
      $.get("/get_results").then(results => {
        console.log(JSON.parse(results));
      });
    });
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
