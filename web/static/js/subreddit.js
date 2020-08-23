function addRecentLocked(posts) {
    var div = document.getElementById("recent_locked_posts");
    var table = document.createElement("table");
    table.style.width = "100%";
    table.id = "recent_locked_posts";

    var tr = table.insertRow();
    var th = document.createElement("th");
    th.appendChild(document.createTextNode("Subreddit"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Title"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Date created"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Date locked"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Original"));
    th.classList.add("table_link");
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Crosspost"));
    th.classList.add("table_link");
    tr.appendChild(th);

    maxlength = 20;
    if (posts.length < 20)
        maxlength = posts.length;

    for (var row = 0; row < maxlength; row++) {
        var tr = table.insertRow();
        for (var column = 0; column < 6; column++) {
            if (row == posts.length + 1 && column == 5) {
                break;
            } else {
                var td = tr.insertCell();
                if (column == 0) {
                    td.appendChild(document.createTextNode("r/"+posts[row].subreddit));
                } else if (column == 1) {
                    td.classList.add("recent_title")
                    td.appendChild(document.createTextNode(posts[row].title));
                } else if (column == 2) {
                    var date = moment(new Date(Number(posts[row].created_utc)* 1000)).format('DD/MM/YYYY h:mm:ss');
                    td.appendChild(document.createTextNode(date));
                } else if (column == 3) {
                    var date = moment(new Date(Number(posts[row].locked_utc)* 1000)).format('DD/MM/YYYY h:mm:ss');
                    td.appendChild(document.createTextNode(date));
                } else if (column == 4) {
                    img = document.createElement("img");
                    img.src = PREFIX + "/static/img/link.svg";
                    img.classList.add("recent_link");
                    a = document.createElement("a");
                    a.appendChild(img);
                    a.href = "https://np.reddit.com/r/"+ posts[row].subreddit + "/comments/" + posts[row].id;
                    td.classList.add("recent_link");
                    td.appendChild(a);
                } else if (column == 5) {
                    img = document.createElement("img");
                    img.src = PREFIX + "/static/img/link.svg";
                    img.classList.add("recent_link");
                    a = document.createElement("a");
                    a.appendChild(img);
                    a.href = "https://reddit.com" + posts[row].crosspost;
                    td.classList.add("recent_link");
                    td.appendChild(a);
                }
            }
        }
    }

    div.replaceWith(table);
}

function removeData(chart, chart_data) {
    chart.data.labels = chart_data.labels;
    chart.data.datasets[0].data = chart_data.unlocked_posts
    chart.data.datasets[1].data = chart_data.locked_posts
    chart.update();
}

function addChart(posts) {
    var labels = [];
    for (const post of posts){
        if (post.locked_utc != "0")
            labels.push(moment(new Date(Number(post.locked_utc)*1000)).format("MM/DD/YY"));
    }

    const map = labels.reduce((acc, e) => acc.set(e, (acc.get(e) || 0) + 1), new Map());

    var labels_clean = []
    for (label of [...map.keys()].reverse()) {
        labels_clean.push(moment(label, "MM/DD/YY"));
    }

    ctx = document.getElementById("locked_chart")
    locked_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels_clean,
            datasets: [{ 
                data: [...map.values()].reverse(),
                label: "Locked post",
                borderColor: "rgba(75, 192, 192, 0.7)",
                fill: false,
                lineTension: 0
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            quarter: 'DD MMM YYYY'
                        }
                    }
                }],
                yAxes: [{
                    ticks: {
                      stepSize: 1,
                      beginAtZero: true
                    }
                }]              
            }
        }
    });
}

const PREFIX = ""

$.get(PREFIX + "/api/r/" + subreddit + "?locked=true&limit=", function(data, status) {
    addRecentLocked(data.posts);
    addChart(data.posts)
});

var ctx, locked_chart;
