//var group_id = "1732457";

d3.json("/group/" + group_id + "/users", function(error, group) {

    group.sort(function(a,b) { return d3.ascending(a.nickname, b.nickname); }).forEach(function(d,i) { d.index = i; });
    var ROWS = 5;
    var WIDTH = 232;

    var top = function(d,i) {
        return (Math.floor(i / ROWS) * 100) + "px";
    };
    var left = function(d, i) {
        return (i % ROWS) * WIDTH + "px";
    };

    var overview = d3.select("#overview")
                        .selectAll("div")
                        .data(group)
                        .enter().append("div").attr("class", "user-info").style("top", top).style("left", left)
                        .style("width", 500 + "px").style("overflow", "visible");

    d3.select("#overview").style("height", function() { return (Math.ceil(group.length/ROWS) * 100 + 20) + "px"});

    overview.append("img").attr("class", "img-circle pull-left").attr("src", function(d) {
            if(d.image_url)
                return d.image_url;
            else
                return "/static/img/question-mark.jpg";
        })
        .style("width" , "80px").style("height", "80px");


        overview.on("click", function(d, i) {
            var currentRow = Math.floor(d.index / ROWS);
            var clicked = d;
            var active = d3.select(this).classed("active");
            d3.selectAll(".user-sparkcharts").style("display", "none");
            d3.select("#user-sparkcharts-" + d.user_id).style("display", active ? "none":"inline");
            d3.select(this).classed("active", !active);
            var index = d.index;
            overview.transition().duration(350).style("left", function(d2, i2) {
                if(!active && i2 > index && Math.floor(i2/ROWS) === currentRow) {
                    if((i2+1) % ROWS === 0) {
                        return ROWS * WIDTH + "px";
                    }
                    return left(null, i2 + 1);
                } else if(!active && (index+1) % ROWS == 0 && Math.floor(i2/ROWS) === currentRow) {
                    if((i2-1) < 0 || i2 % ROWS === 0) {
                        return -1 * WIDTH + "px";
                    }
                    return left(null, i2 - 1);
                } else {
                    return left(null, i2);
                }
            });
        });

    var user_text = overview.append("div").attr("class", "user-text pull-left");
    user_text.append("p").text(function(d) { return d.nickname; });
    user_text.append("p").html(function(d) {
        var percentage  = parseFloat(d.msg_perc * 100).toFixed(4).toString().split(".");
        var finalPerc = percentage[0] + "." + percentage[1].substr(0,2);
        return "<strong>Sent: </strong>" + d.msgs_per + " (" + finalPerc + "%)";
    });
    user_text.append("p").html(function(d) { return "<strong>PowerRank: </strong>" + parseFloat(Math.round(d.prank * 100) / 100).toFixed(2); });
    user_text.append("p").html(function(d) { return "<strong>Likes Per Msg: </strong>" + parseFloat(Math.round((d.msgs_per/d.likes_rec) * 100) / 100).toFixed(3); });
    user_text.append("p").html(function(d) { return "<strong>Rec.: </strong>" + d.likes_rec + ", <strong>Given: </strong>" + d.likes_give;  });
    user_text.append("p").html(function(d) { return  });
    user_text.append("p").html(function(d) { return "<strong>Ratio: </strong>" + parseFloat(Math.round((d.likes_rec/d.likes_give) * 100) / 100).toFixed(4); });

    overview.append("div").attr("class", "user-sparkcharts pull-left").attr("id", function(d) { return "user-sparkcharts-" + d.user_id; })
            .html(function(d, i) {
                return '<small><em>30-day trends</em></small><div><div class="sparkchart-wrap">' +
                '<small style="font-size: 80%;">Likes</small><div class="sparkchart" id="spark-likes-' + d.user_id + '"></div></div>' +
                '<div class="sparkchart-wrap"><small style="font-size: 80%;">Messages</small>' +
                '<div class="sparkchart" id="spark-messages-' + d.user_id + '"></div></div></div>';
            });


    function reSort(field) {
        function sort_func(a, b) {
            if(field != 'nickname')
                return d3.descending(parseFloat(a[field]), parseFloat(b[field]));
                else
                    return d3.ascending(a[field], b[field]);
        }
        group.sort(sort_func).forEach(function(d,i) { d.index = i; });
        overview.sort(sort_func).transition().duration(500).style("top", top).style("left", left);
    }

    group.forEach(function(u) {
        renderSparkline(u.user_id);
    });

    //on change function i need to control selected value
    $('#member-sort').on('change', function(){
        var selected = $('.selectpicker option:selected').val();
        reSort(selected);
    });
});
