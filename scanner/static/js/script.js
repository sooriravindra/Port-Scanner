$(document).ready(() => {
  //show results
  $.get("/get_results").then(renderResults);

  $("#scan_request").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".spinner").show();

    console.log(data);

    $.post("/port_scan", data).then(submitSuccess.bind(null, "port_scan"));
  });

  $("#check_live_hosts").submit(function(event) {
    event.preventDefault();
    const data = $(this).serialize();
    $(".spinner").show();
    console.log(data);
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

    if (results[jobId]['open_hosts'].length > 0) {
      if ($("#hosts_"+jobId).length == 0) {
        //The open hosts table doesn't exist yet
        var resultBody = getResultBody(jobId,results[jobId]['task_type']);
        $("#button_"+jobId).parent().append(resultBody);
      }
      $("#hosts_"+jobId).html("");
      let i = 1;
      for(let open_host in results[jobId]['open_hosts']) {
        var resultRow = getResultRow(i,results[jobId]['task_type'],results[jobId]['open_hosts'][open_host]);
        $("#hosts_"+jobId).append(resultRow);
        i++;
      }
    }
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
            <th scope="col">IP Address</th>
            <th scope="col">Port</th>
            <th scope="col">Banner</th>`;
  }
};

const getResultRow = (index,task_type,hostData) => {
  if (task_type == "Normal Scan") {
    console.log(hostData);
    return `<tr>
              <td>`+index+`</td>
              <td>`+hostData['ip']+`</td>
              <td>`+hostData['port']+`</td>
              <td>`+hostData['payload']+`</td>
            </tr>`;
  }
};

const getResultBody = (id,task_type) => {
  var header = getResultHeader(task_type);
  var table = `<div id="collapse{id}" class="collapse" data-parent="#accordion">
                  <div class="card-body">
                    <table class="table table-striped">
                      <thead>
                        <tr>
                          {header}
                        </tr>
                      </thead>
                      <tbody id="hosts_{id}">
                      </tbody>
                    </table>
                  </div>
                </div>`;
  table = table.replaceAll("{id}",id);
  table = table.replace("{header}",header);
  return table;
};
