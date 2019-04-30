$(document).ready(() => {


  $("#scan_request").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".formdiv").hide();
    $(".spinner").show();

    $.post("/submit_task", data).then(status => {
      $(".spinner").hide();
      $(".results").show();
      $.get("/get_results").then(results => JSON.parse(results).forEach(render));
    });

  });
});

// <th scope="col">Scan Type</th>
// <th scope="col">Status</th>
// <th scope="col">Payload</th>

const render = data => {
  const ip = data["ip"];
  const port = data["port"];
  const taskStatus = data["task_status"];
  const scanType = data["scan_type"];
  const scanResult = data["scan_result"];
  const portStatus = scanResult["status"];
  const scanPayload = scanResult["payload"];

  const results = $("#scan-results");
  const length = results.length;

  const row = $("<tr/>");
  const idCell = $("<td/>");
  const ipCell = $("<td/>");
  const portCell = $("<td/>");
  const taskStatusCell = $("<td/>");
  const scanTypeCell = $("<td/>");
  const portStatusCell = $("<td/>");
  const scanPayloadCell = $("<td/>");

  idCell.append(length);
  ipCell.append(ip);
  portCell.append(port);
  taskStatusCell.append(taskStatus);
  scanTypeCell.append(scanType);
  portStatusCell.append(portStatus);
  scanPayloadCell.append(scanPayload);

  row.append(idCell);
  row.append(ipCell);
  row.append(portCell);
  row.append(scanTypeCell);
  row.append(taskStatusCell);
  row.append(portStatusCell);
  row.append(scanPayloadCell);

  results.append(row);
};
