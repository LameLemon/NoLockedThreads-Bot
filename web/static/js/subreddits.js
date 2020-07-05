function addRecentLocked(posts) {
    var div = document.getElementById("recent_locked_posts");
    var table = document.createElement("table");
    table.style.width = "100%";
    table.id = "recent_locked_posts";

    var thead = document.createElement("thead");
    var tr = document.createElement("tr");
    var th = document.createElement("th");
    th.appendChild(document.createTextNode("Subreddit"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Total posts"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Locked posts"));
    tr.appendChild(th);

    th = document.createElement("th");
    th.appendChild(document.createTextNode("Unlocked posts"));
    tr.appendChild(th);

    thead.appendChild(tr);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    for (var row = 0; row < posts.length; row++) {
        var tr = document.createElement("tr");
        for (var column = 0; column < 4; column++) {
            if (row == posts.length + 1 && column == 3) {
                break;
            } else {
                var td = document.createElement("td");
                if (column == 0) {
                    var a = document.createElement("a");
                    a.text = "r/" + posts[row].subreddit;
                    a.href = a.text;
                    td.appendChild(a);
                } else if (column == 1) {
                    td.classList.add("recent_link");
                    td.appendChild(document.createTextNode(posts[row].total_posts));
                } else if (column == 2) {
                    td.classList.add("recent_link");
                    td.appendChild(document.createTextNode(posts[row].locked_posts));
                } else if (column == 3) {
                    td.classList.add("recent_link");
                    td.appendChild(document.createTextNode(posts[row].unlocked_posts));
                }
            }
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    div.replaceWith(table);
}

const PREFIX = ""

$.get(PREFIX + "/api/r/all/count?limit=100", function(data, status) {
    console.log(data);
    addRecentLocked(data.stats);
    $('#recent_locked_posts').DataTable({
        "paging": false,
        "info": false,
        "order": [[ 1, "desc" ]]
    });
  
});
