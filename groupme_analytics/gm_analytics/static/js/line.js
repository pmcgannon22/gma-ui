var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 900 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse;

var x = d3.time.scale()
    .range([10, width-10]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.msgs); });
var svg;
var point = function() {
        this.attr("transform", function(d) {
		    return "translate(" + x(d.date) + "," + y(d.msgs) + ")";
        });
    };

d3.json("/group/1732457/dailydata?limit=35", function(error, data) {
    data.forEach(function(d) {
        d.date = parseDate(d.date);
        d.msgs = +d.msgs;
    });

    x.domain(d3.extent(data, function(d) { return d.date; }));
    y.domain([0, d3.max(data, function(d) { return d.msgs; })]);

/*    var zoom = d3.behavior.zoom()
        .x(x)
        .y(y)
        .on("zoom", zoomed);*/

    d3.select("#daily").append("button")
        .text("Reset")
        .attr("class", "btn btn-small");
/*
        .on("click", function() {
            zoom.translate([0,0]).scale(1);
            zoomed();
        });*/

    svg = d3.select("#daily").append("svg")//.call(zoom)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.sort(function(a,b) { return a.date - b.date; });


    svg.append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("# of Messages");

  svg.append("g")
      .append("path")
      .datum(data)
      .attr("clip-path", "url(#clip)")
      .attr("class", "line")
      .style("stroke","steelblue")
      .attr("d", line);
    var points = svg.selectAll(".points").data(data).enter()
        .append("g")
        .attr("class", "points")
        .attr("clip-path", "url(#clip)");

    points.selectAll(".point")
        .data(data)
        .enter().append("circle")
        .attr("class", "point")
        .attr("r", 3)
        .attr("title", function(d) {
            return (d.date.getMonth()+1) + "/" + d.date.getDate() + "/" + d.date.getFullYear() + ": " + d.msgs;
        }).style("fill", "steelblue")
        .call(point);

    $(".point").tooltip({
        'container':'body',
        'placement':'top'
    });

});



function zoomed() {
    svg.select(".x.axis").call(xAxis);
    svg.select(".y.axis").call(yAxis);
    svg.select(".line")
        .attr("class", "line")
        .attr("d", line);
    svg.selectAll(".point").call(point);
}
