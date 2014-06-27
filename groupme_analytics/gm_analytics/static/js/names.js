var margin = {top: 20, right: 5, bottom: 30, left: 5},
width = 900 - margin.left - margin.right,
height = 275 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse,
    formatDate = d3.time.format("%b %d"),
    bisectDate = d3.bisector(function(d) { return d.begin; }).left;

var x = d3.time.scale()
.range([10, width-10]);

var y = d3.scale.linear()
.range([height-10, 10]);

var xAxis = d3.svg.axis()
.scale(x)
.orient("bottom");


var color = d3.scale.category20();

var svg = d3.select("#names").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("/group/" + group_id + "/names", function(error, data) {

    data.forEach(function(d) {
        d.begin = parseDate(d.begin);
        d.end = parseDate(d.end);
    });

    x.domain([data[0].begin, data[data.length-1].end]);

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

    svg.selectAll("rect")
        .data(data).enter()
        .append("rect")
        .attr("x", function(d) { return x(d.begin); })
        .attr("y", height - 50)
        .attr("width", function(d) { return x(d.end) - x(d.begin); })
        .attr("height", 40)
        .attr("title", function(d) { return d.name; })
        .style("fill", function(d, i) { return color(d.name); });

    var focus = svg.append("g")
      .attr("class", "focus")
      .style("display", "none");

    focus.append("line")
        .attr("class","tracker")
        .attr("y1", 150).attr("y2", height - 10);

    var labelY = 50;

    focus.append("text").attr("class","current")
      .attr("x", width/2)
      .attr("y", labelY);
    focus.append("text").attr("class","current-date .name-date")
        .attr("x", width/2)
        .attr("y", labelY + 20);
    focus.append("rect").attr("class", "current-color")
        .attr("x", width/2 - 50).attr("width", 100)
        .attr("y", labelY + 35).attr("height", 10);

    focus.append("text").attr("class", "previous")
        .attr("x", 100)
        .attr("y", labelY);
    focus.append("text").attr("class","previous-date .name-date")
        .attr("x", 100)
        .attr("y", labelY + 20);
    focus.append("rect").attr("class", "previous-color")
        .attr("x", 50).attr("width", 100)
        .attr("y", labelY + 35).attr("height", 10);

    focus.append("text").attr("class", "next")
        .attr("x", width - 100)
        .attr("y", labelY);
    focus.append("text").attr("class","next-date name-date")
        .attr("x", width - 100)
        .attr("y", labelY + 20);
    focus.append("rect").attr("class", "next-color")
        .attr("x", width - 150).attr("width", 100)
        .attr("y", labelY + 35).attr("height", 10);

    svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() { focus.style("display", null); })
      .on("mouseout", function() { focus.style("display", "none"); })
      .on("mousemove", mousemove);

  function mousemove() {
    var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(data, x0, 1);
    focus.select(".tracker").attr("transform", "translate(" + d3.mouse(this)[0] + ")");

    focus.select(".current").text(data[i - 1].name);
    focus.select(".current-date").text(formatDate(data[i-1].begin) + " – " + formatDate(data[i-1].end));
    focus.select(".current-color").style("fill", color(data[i-1].name));

    focus.select(".previous").text(i > 1 && i <= data.length ? data[i-2].name : "");
    focus.select(".previous-date").text(i > 1 && i <= data.length ? formatDate(data[i-2].begin) + " – " + formatDate(data[i-2].end) : "");
    focus.select(".previous-color").style("fill", i > 1 && i <= data.length ? color(data[i-2].name) : "white");

    focus.select(".next").text(i >= 0 && i < data.length ? data[i].name : "");
    focus.select(".next-date").text(i >= 0 && i < data.length ? formatDate(data[i].begin) + " – " + formatDate(data[i].end) : "");
    focus.select(".next-color").style("fill", i >= 0 && i < data.length ? color(data[i].name) : "white");
    //focus.attr("transform", "translate(" + x(d.date) + "," + y(d.close) + ")");
    //focus.select("text").text(formatCurrency(d.close));
  }
    /*
    svg.selectAll(".label")
        .data(data).enter()
        .append("text")
        .attr("class", "label")
        .attr("x", function(d) { return (x(d.begin) + x(d.end)) / 2; })
        .attr("y", function(d,i) {

        })
        .attr("text-anchor", "middle")
/       .attr("transform", function(d) {
            return "rotate(90 " + this.getAttribute("x") + "," + this.getAttribute("y") + ")";
        })
        .text(function(d) { return d.name; });*/



});
