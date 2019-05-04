$(document).ready(() => {
  //show results
  $.get("/get_results").then(renderResults);

  $("#scan_request").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".spinner").show();

    $.post("/port_scan", data).then(status => {
      $(".spinner").hide();
      $("#scan_request_modal").modal("hide");
    });
  });
});

$("#check_live_hosts").submit(function(event) {
  event.preventDefault();
  const data = $(this).serialize();
  $(".spinner").show();
  $.post("/ping_scan", data).then(status => {
    $(".spinner").hide();
    $("#check_live_hosts_modal").modal("hide");
  });
});

const renderResults = results => {
  results = JSON.parse(results);
  const resultsParent = $("#scan-results");

  for (let jobId in results) {
    const jobTitle = getJobTitleRow(jobId, results[jobId]['task_type']);
    resultsParent.append(jobTitle);

    const openHosts = $("<tr>", {
      id: `collapse${jobId}`,
      class: "panel-collapse collapse"
    });

    (results[jobId]['open_hosts'] || []).forEach(result => {
      const row = getResultRow(result);
      openHosts.append(row);
    });

    resultsParent.append(openHosts);
  }
};

const getJobTitleRow = (id, task_type) => {
  const row = $("<tr>", {
    class: "job-title",
    "data-toggle": "collapse",
    href: `#collapse${id}`
  });
  const column = $("<td>", {
    text: `Request ${task_type} ${id}`
  });

  row.append(column);
  return row;
};

const getResultRow = data => {
  const portStatus = data["status"];
  const scanPayload = data["payload"];
  const ip = data["ip"];
  const port = data["port"];

  const row = $("<tr>");
  const ipCell = $("<td>", {
    text: ip
  });
  const portCell = $("<td>", {
    text: port
  });
  const portStatusCell = $("<td>", {
    text: portStatus
  });
  const scanPayloadCell = $("<td>", {
    text: scanPayload
  });

  row.append(ipCell);
  row.append(portCell);
  row.append(portStatusCell);
  row.append(scanPayloadCell);

  return row;
};
