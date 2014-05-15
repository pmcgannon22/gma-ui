var w = 850,
    h = 500,
    fill = d3.scale.category20();

d3.text("/group/3547964/words/100", function(error, data) {
    var wrds = data.split(" ");
    console.log(wrds);
    d3.layout.cloud().size([w, h])
      .words(wrds.map(function(d) { return {text: d}; }))
      .padding(5)
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .font("Impact")
      .fontSize(function(d) { return d.size; })
      .on("end", draw)
      .start();
});


function draw(words) {
    console.log(words);
    d3.select("#cloud").append("svg")
        .attr("width", w)
        .attr("height", h)
        .append("g")
        .attr("transform", "translate(150,150)")
        .selectAll("text")
        .data(words)
        .enter().append("text")
        .style("font-size", function(d) { return 10 + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { console.log(d); return d.text; });
}
