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

const updateRow = (id,resultCount) => {
  var disabled = "disabled";
  var result = "<span class='badge badge-success'>Closed</span>";
  if (resultCount > 0) {
    disabled = "";
    result = "Open <span class='badge badge-pill badge-danger'>"+resultCount+"</span>";
  }
  $("#result_"+id).html(result);
  $("#button_"+id).addClass(disabled);
};

var renderedIds = [];
const renderResults = results => {
  results = JSON.parse(results);
  console.log(results);

  if ($.isEmptyObject(results)) {
    return;
  }

  $("#scan-results")[0].style.display="initial";

  const container = $("#accordion");

  for (let jobId in results) {
    if (!renderedIds.includes(jobId)) {
      renderedIds.push(jobId);
      const jobTitle = getJobTitleRow(jobId, results[jobId]);
      const parentDiv = $("<div>");
      parentDiv.append(jobTitle);
      container.append(parentDiv);
    }
    updateRow(jobId,results[jobId]['open_hosts'].length);
    /*
    const openHosts = $("<tr>", {
      id: `collapse${jobId}`,
      class: "panel-collapse collapse"
    });

    (results[jobId]["open_hosts"] || []).forEach(result => {
      const row = getResultRow(result);
      openHosts.append(row);
    });

    container.append(openHosts);
    */
  }
};

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

const getJobTitleRow = (id, resultRow) => {
  
  var element = `<button id="button_{id}" class="list-group-item list-group-item-action" data-toggle="collapse"
              data-target="#collapse{id}" aria-expanded="true" aria-controls="collapse{id}">
                  <div class="row">
                      <div class="col">{id}</div>
                      <div class="col">{ip_address}</div>
                      <div class="col">{start_port}</div>
                      <div class="col">{end_port}</div>
                      <div class="col">{subnet}</div>
                      <div class="col">{task_type}</div>
                      <div id="result_{id}" class="col"></div>
                  </div>
              </button>`;
  element = element.replaceAll("{id}",id);
  element = element.replace("{ip_address}",resultRow['ip_address'])
  element = element.replace("{start_port}",resultRow['start_port']);
  element = element.replace("{end_port}",resultRow['end_port']);
  element = element.replace("{subnet}",resultRow['subnet']);
  element = element.replace("{task_type}",resultRow['task_type']);

  return element;
};

const getResultHeader = (task_type) => {
  if (task_type == "Normal Scan") {
    return `<th scope="col">#</th>
            <th scope="col">First</th>
            <th scope="col">Last</th>
            <th scope="col">Handle</th>`;
  }
};

const getResultRow = data => {
  var rowElem = `<tr>
              <th scope="row">1</th>
              <td>Mark</td>
              <td>Otto</td>
              <td>@mdo</td>
            </tr>`;

  var table = `<div id="collapse{id}" class="collapse" data-parent="#accordion">
                  <div class="card-body">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          {header}
                        </tr>
                      </thead>
                      <tbody>
                      </tbody>
                    </table>
                  </div>
                </div>`;

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
