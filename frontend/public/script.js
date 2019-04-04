function sleep(time) {
    console.log("Inside sleep");
    return new Promise(resolve => setTimeout(resolve, time));
}

function onScan() {
    console.log("Inside onScan");

    // Hide form and show spinner
    $(".formdiv").hide();
    $(".spinner").show();

    // Display results table after 4s for now
    sleep(4000).then(() => {
        console.log("Resolved sleep");
        $(".spinner").hide();
        $(".results").show();
    });

    // Return false to prevent form submission
    return false;
}
