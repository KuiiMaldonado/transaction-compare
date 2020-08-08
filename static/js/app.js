//Variable to store the data received from the enpoint /reconciliation
var response;

//Reference to the unmatched-button element
var unmatchedButton = d3.select("#unmatched-button");

//Reference to the table head element of unmtached-table
var unmatched_tHead = d3.select("#unmatched-table > thead");

//Reference to the table body element of unmatched-table
var unmatched_tBody = d3.select("#unmatched-table > tbody");

//Reference to the table head of possible-table
var possible_tHead = d3.select("#possible-table > thead")

//Reference to the table body of possible-table
var possible_tBody = d3.select("#possible-table > tbody")

//Function for detecting the submit of the form and upload the files to flask application
$(function(){
    $("#formUpload").on("submit", function(d){
        d.preventDefault();
        var f = $(this);
    
        var formData = new FormData(document.getElementById("formUpload"));
        
        $.ajax({
            url: "/reconciliation",
            type: "post",
            data: formData,
            cache: false,
            contentType: false,
            processData: false
        }).then(data => {
            //Updating the numbers of mateches, etc on each file card
            updateFile1(data);
            updateFile2(data);
            response = data;
        });
    });
});

//Function to create both tables (unmatched reports and possible match reports)
function showTables()
{
    showUnmatchedTable();
    showPossibleTable();
}

//Function to create the headers of the unmtached table depending on how it is received on the response
function tableHeaders()
{
    var row = unmatched_tHead.append("tr");
    Object.entries(response["unmatched"]["0"]).forEach(([key, value]) => {
        var cell = row.append("th").classed("table-head", true);
        cell.text(key);
    });
}

//Function to display the headers for possible matches table in a specific format
function customTableHeaders()
{
    //Append a row to display the name of the different files as table headers
    var row = possible_tHead.append("tr");
    //First file header
    var cell = row.append("th").attr("colspan", "4").classed("table-head", true);
    cell.text(response["file1"]["name"]);
    //Second file header
    cell = row.append("th").attr("colspan", "4").classed("table-head", true);
    cell.text(response["file2"]["name"]);

    //Append a row to display de columns name in the desired order
    row = possible_tHead.append("tr");

    //Transaction ID for file one
    cell = row.append("th").classed("table-head", true);
    cell.text("TransactionID");
    //Date for file one
    cell = row.append("th").classed("table-head", true);
    cell.text("Date");
    //Amount for file one
    cell = row.append("th").classed("table-head", true);
    cell.text("Amount");
    //Narrative for file one
    cell = row.append("th").classed("table-head", true);
    cell.text("Narrative");

    //Transaction ID for file two
    cell = row.append("th").classed("table-head", true);
    cell.text("TransactionID");
    //Date for file two
    cell = row.append("th").classed("table-head", true);
    cell.text("Date");
    //Amount for file two
    cell = row.append("th").classed("table-head", true);
    cell.text("Amount");
    //Narrative for file two
    cell = row.append("th").classed("table-head", true);
    cell.text("Narrative");
}

//Function to create and fill the unmatched reports table
function showUnmatchedTable()
{
    tableHeaders();
    Object.entries(response["unmatched"]).forEach(element => {
        var row = unmatched_tBody.append("tr");
        Object.entries(element[1]).forEach(([key, value]) => {
            var cell = row.append("td");
            cell.text(value);
        });
    });
}

//Function to create and fill possible reports matches table using the specific design for this table
function showPossibleTable()
{
    customTableHeaders();
    Object.entries(response["possible"]).forEach(element => {
        var row = possible_tBody.append("tr");
        console.log(`${element[1]["TransactionID"]}`);

        //TransactionID file one
        var cell = row.append("td");
        cell.text(element[1]["TransactionID"]);
        //TransactionDate file one
        var cell = row.append("td");
        cell.text(element[1]["TransactionDate"]);
        //TransactionAmount file one
        var cell = row.append("td");
        cell.text(element[1]["TransactionAmount"]);
        //TransactionNarrative file one
        var cell = row.append("td");
        cell.text(element[1]["TransactionNarrative"]);

        //TransactionID file two
        var cell = row.append("td");
        cell.text(element[1]["TransactionID_2"]);
        //TransactionDate file two
        var cell = row.append("td");
        cell.text(element[1]["TransactionDate_2"]);
        //TransactionAmount file two
        var cell = row.append("td");
        cell.text(element[1]["TransactionAmount_2"]);
        //TransactionNarrative file two
        var cell = row.append("td");
        cell.text(element[1]["TransactionNarrative_2"]);
    });
}

function updateFile1(data)
{
    var element = d3.select("#file1-title");
    element.text(data.file1.name);

    element = d3.select("#file1-total");
    element.text(`Total Records: ${data.file1.total}`);

    element = d3.select("#file1-match");
    element.text(`Perfect Matches: ${data.file1.matches}`);

    element = d3.select("#file1-possible");
    element.text(`Possible Matches: ${data.file1.possible}`);

    element = d3.select("#file1-unmatch");
    element.text(`Unmatched: ${data.file1.mismatches}`);
}

function updateFile2(data)
{
    var element = d3.select("#file2-title");
    element.text(data.file2.name);

    element = d3.select("#file2-total");
    element.text(`Total Records: ${data.file2.total}`);

    element = d3.select("#file2-match");
    element.text(`Perfect Matches: ${data.file2.matches}`);

    element = d3.select("#file2-possible");
    element.text(`Possible Matches: ${data.file2.possible}`);

    element = d3.select("#file2-unmatch");
    element.text(`Unmatched: ${data.file2.mismatches}`);
}

//Listener for the button to show tables
unmatchedButton.on("click", showTables);