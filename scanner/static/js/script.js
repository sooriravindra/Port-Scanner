$(document).ready(() => {
  //show results
  $.get("/get_results").then(renderResults);

  $("#scan_request").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".spinner").show();

    $.post("/port_scan", data).then(submitSuccess.bind(null, "port_scan"));
  });

  $("#check_live_hosts").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".spinner").show();
    $.post("/ping_scan", data).then(submitSuccess.bind(null, "ping_scan"));
  });

  $("#refresh-data").click(event => {
    $.get("/get_results").then(renderResults);
  });
});

const submitSuccess = (requestType, status) => {
  const modalId =
    requestType === "port_scan"
      ? "#scan_request_modal"
      : "#check_live_hosts_modal";
  $(".spinner").hide();
  $(modalId).modal("hide");

  status = JSON.parse(status);
  if (status.status === "OK") {
    toastr.success(
      "Please click on the refresh button to see updated results",
      "Request Submitted"
    );
  } else {
    toastr.error(status.message);
  }

  $.get("/get_results").then(renderResults);
};

const renderResults = results => {
  results = JSON.parse(results);
  const resultsParent = $("#scan-results");
  resultsParent.html("");

  for (let jobId in results) {
    const jobTitle = getJobTitleRow(jobId, results[jobId]["task_type"]);
    resultsParent.append(jobTitle);

    const openHosts = $("<tr>", {
      id: `collapse${jobId}`,
      class: "panel-collapse collapse"
    });

    (results[jobId]["open_hosts"] || []).forEach(result => {
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
