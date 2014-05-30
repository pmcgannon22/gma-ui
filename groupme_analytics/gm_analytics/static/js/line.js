    var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 900 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    var parseDate = d3.time.format("%Y-%m-%d").parse;

    var x = d3.time.scale()
    .range([10, width-10]);

    var y = d3.scale.linear()
    .range([height-10, 10]);

    var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

    var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

    var color = d3.scale.category10();

    var line = d3.svg.line()
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.total); });
    var svg;
    var point = function() {
        this.attr("transform", function(d) {
    	    return "translate(" + x(d.date) + "," + y(d.total) + ")";
        });
    };

    d3.json("/group/"+group_id+"/dailydata?limit=35", function(error, data) {
    color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));

    data.forEach(function(d) {
        d.date = parseDate(d.date);
    });

    var cats = color.domain().map(function(name) {
        return {
          name: name,
          values: data.map(function(d) {
            return {date: d.date, total: +d[name]};
          })
        };
      });

    x.domain(d3.extent(data, function(d) { return d.date; }));
    y.domain([
        d3.min(cats, function(c) { return d3.min(c.values, function(v) { return v.total; }); }),
        d3.max(cats, function(c) { return d3.max(c.values, function(v) { return v.total; }); })
      ]);

    svg = d3.select("#daily").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    cats.map(function(c) { return c.values.sort(function(a,b) { return a.date - b.date; }); });

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

    var category = svg.selectAll(".category")
      .data(cats).enter()
      .append("g").attr("class", "category");

    category.append("path")
      .attr("class", "line")
      .style("stroke",function(d) { return color(d.name); })
      .attr("d", function(d) { return line(d.values); });

    category.selectAll(".points")
        .data(function(d) { return d.values; })
        .enter().append("circle")
        .attr("class", "point")
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d.total); })
        .attr("r", "3px")
        .style("cursor", "pointer")
        .style("fill", function(d, i, j) { return color(cats[j].name) })
        .attr("title", function(d) {
            return (d.date.getMonth()+1) + "/" + d.date.getDate() + "/" + d.date.getFullYear() + ": " + d.total;
        }).on("click", function(d) {
            var date = ('0' + (d.date.getMonth()+1)).slice(-2) + '/' + ('0' + d.date.getDate()).slice(-2) + '/' + d.date.getFullYear();
            $("#conversationModal").modal({'show':true, 'remote':'messages/conversation?day='+date});
        });

    $(".point").tooltip({
        'container':'body',
        'placement':'top'
    });

    var legend = svg.selectAll(".legend")
        .data(cats.map(function(d) { return d.name; }))
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function (d, i) { return "translate(-25," + (i * 20 + 50) + ")"; });

    legend.append("rect")
        .attr("x", width - 10)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", color)
        .style("stroke", "grey");

    legend.append("text")
        .attr("x", width - 15)
        .attr("y", 6)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function (d) { return d; });
});



    function zoomed() {
    svg.select(".x.axis").call(xAxis);
    svg.select(".y.axis").call(yAxis);
    svg.select(".line")
        .attr("class", "line")
        .attr("d", line);
    svg.selectAll(".point").call(point);
    }
