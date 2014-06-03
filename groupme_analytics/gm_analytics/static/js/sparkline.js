
function renderSparkline(uid) {
    var width = 100;
    var height = 25;
    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);
    var parseDate = d3.time.format("%Y-%m-%d").parse;

    function sparkchart(data, selector) {
        var line = d3.svg.line()
                     .x(function(d) { return x(d.date); })
                     .y(function(d) { return y(d.total); });

        data.forEach(function(d) {
          d.date = parseDate(d.date);
          d.total = +d.total;
        });
        x.domain(d3.extent(data, function(d) { return d.date; }));
        y.domain(d3.extent(data, function(d) { return d.total; }));

        var svg = d3.select(selector)
          .append('svg')
          .attr('width', width)
          .attr('height', height);
        svg.append('path')
          .datum(data)
          .attr('class', 'sparkline')
          .attr('d', line);
        if(!data.length) {
            svg.append("line")
                    .attr("x1", 0)
                    .attr("y1", height)
                    .attr("x2", width)
                    .attr("y2", height)
                    .style("stroke", "black").style("stroke-width","0.5px");
        }
    }


    d3.json('/group/' + group_id + '/user?limit=75&uid='+uid, function(error, data) {
        ['likes','messages'].forEach(function(k) {
            sparkchart(data[k], '#spark-' + k + '-' + uid);
        });
    });
}
