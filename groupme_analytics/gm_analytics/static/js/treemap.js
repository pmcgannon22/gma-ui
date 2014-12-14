var margin = {top:0, right:0, bottom: 0, left: 0},
    w = 850 - margin.left - margin.right,
    h = 500 - margin.top - margin.bottom,
    formatNumber = d3.format(",d"),
    color = d3.scale.category20c();

    var treemap = d3.layout.treemap()
            .size([w, h])
            .sticky(true)
            .value(function(d) { return d.messages; });

    var tree = d3.select("#tree").append("svg")
            .style("width", w)
            .style("height", h)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .style("shape-rendering", "crispEdges");

d3.json("/group/" + group_id + "/percentages", function(error, json) {

    var node = tree.datum(json)
        .selectAll(".cell")
        .data(treemap.nodes)
        .enter().append("g")
        .attr("class", "cell");

    node.append("rect")
        .call(position)
        .style("fill", function(d, i) { return color(i);});



    node.append("text")
        .attr("class", "name")
        .attr("x", function(d) { return d.dx > 60 ? d.x + 10 : d.x + 2; })
        .attr("y", function(d) { return d.dy > 30 ? d.y + 20 : d.y + 12; })
        .text(function(d) { return d.name; })
        .style("font-size", function(d) { return Math.min(12, fitText(this, d.dx, d.dy, 12)); });

    node.append("text")
        .attr("class", "value")
        .text(function(d) { return d.value + "%"; })
        .attr("x", function(d) { return d.x + d.dx/2; })
        .attr("y", function(d) { return d.y + d.dy/2; })
        .attr("text-anchor", "middle")
        .style("font-size", function(d) { return Math.min(12, fitText(this, d.dx, d.dy, 12)); })
        .style("display", function(d) { return (d.dy < 55 || d.dx < 50) ? "none" : ""; });

    $(".cell > rect").tooltip({
            'container':'body',
            'placement':'right'
        });
    d3.selectAll(".percentage li").on("click", function change() {
        console.log(json);
        d3.selectAll(".percentage li").attr("class", "");
        d3.select(this).attr("class", "active");
        var id = this.id;
        node
            .data(treemap.value(function(d) { return d[id]; }).nodes)
            .selectAll("rect")
            .transition()
            .duration(1500)
            .attr("data-original-title", function(d) { return d.name + ":" + d.value + "%"; })
            .call(position)

        node
            .selectAll(".name")
            .transition()
            .duration(1500)
            .attr("x", function(d) { return d.x + 10; })
            .attr("y", function(d) { return d.y + 20; })
            .text(function(d) { return d.name; })
            .style("font-size", function(d) { return Math.min(12, fitText(this, d.dx, d.dy, 12)); });
        node
            .selectAll(".value")
            .transition()
            .duration(1500)
            .text(function(d) { return d.value + "%"; })
            .attr("x", function(d) { return d.x + d.dx/2; })
            .attr("y", function(d) { return d.y + d.dy/2; })
            .style("font-size", function(d) { return Math.min(12, fitText(this, d.dx, d.dy, 12)); })
            .style("display", function(d) { return (d.dy < 35 || d.dx < 50) ? "none" : ""; });

    });
});

function position() {
    this.attr("width", function(d) { return d.dx; })
    .attr("height", function(d) { return d.dy; })
    .attr("x", function(d) { return d.x; })
    .attr("y", function(d) { return d.y; })
    .attr("title", function(d) {
        if($(this).attr('data-original-title'))
            $(this).tooltip('hide').attr('data-original-title', d.name + ": " + d.value + "%").tooltip('fixTitle').tooltip('show').tooltip('hide');
        return d.name + ": " + d.value + "%"; });

}

function fitText(element, width, height, font_size) {
    var a = width/element.getBBox().width;
    var b = height/element.getBBox().height;
    return Math.floor(font_size * Math.min(a, b));
}
