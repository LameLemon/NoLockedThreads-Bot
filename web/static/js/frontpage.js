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
    th.appendChild(document.createTextNode("Original"));
    th.classList.add("table_link");
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Crosspost"));
    th.classList.add("table_link");
    tr.appendChild(th);


    for (var row = 0; row < posts.length; row++) {
        var tr = table.insertRow();
        for (var column = 0; column < 5; column++) {
            if (row == posts.length + 1 && column == 4) {
                break;
            } else {
                var td = tr.insertCell();
                if (column == 0) {
                    var a = document.createElement("a");
                    a.text = "r/" + posts[row].subreddit;
                    a.href = a.text;
                    td.appendChild(a);
                } else if (column == 1) {
                    td.classList.add("recent_title")
                    td.appendChild(document.createTextNode(posts[row].title));
                } else if (column == 2) {
                    var date = moment(new Date(Number(posts[row].created_utc)* 1000)).format('MM/DD/YYYY h:mm:ss');
                    td.appendChild(document.createTextNode(date));
                } else if (column == 3) {
                    img = document.createElement("img");
                    img.src = PREFIX + "/static/img/link.svg";
                    img.classList.add("recent_link");
                    a = document.createElement("a");
                    a.appendChild(img);
                    a.href = "https://np.reddit.com/r/"+ posts[row].subreddit + "/comments/" + posts[row].id;
                    td.classList.add("recent_link");
                    td.appendChild(a);
                } else if (column == 4) {
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

function updateChart() {
    $.get(PREFIX + "/api/r/all/count", function(data, status) {
        var chart_data = {
            labels: [],
            unlocked_posts: [],
            locked_posts: []
        }
        for (const sub of data["stats"]) {
            chart_data.labels.push(sub.subreddit);
            chart_data.unlocked_posts.push(sub.unlocked_posts);
            chart_data.locked_posts.push(sub.locked_posts);
        }
        removeData(myChart, chart_data);
    });
    $.get(PREFIX + "/api/r/all?locked=true", function(data, status) {
        addRecentLocked(data.posts);
    });
 
}

const PREFIX = "";

$.get(PREFIX + "/api/r/all?locked=true", function(data, status) {
    addRecentLocked(data.posts);
});

window.setInterval(updateChart, 10000);
var ctx = document.getElementById('top_subs');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: locked_unlocked_data,
    options: {
        legend: {
            labels: {
                fontColor: "white"
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: "white"
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: "white"
                }
            }]
        }
    }
});

var ctx_locked = document.getElementById('top_locked_subs');
var myChart_locked = new Chart(ctx_locked, {
    type: 'bar',
    data: locked_data,
    options: {
        legend: {
            labels: {
                fontColor: "white"
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: "white"
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: "white"
                }
            }]
        }
    }
});