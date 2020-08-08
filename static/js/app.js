var unmatchedButton = d3.select("#unmatched-button");

function showUnmatched()
{
    d3.json("http://127.0.0.1:5000/API").then(data => {
        console.log(data);
    });
}

unmatchedButton.on("click", showUnmatched);