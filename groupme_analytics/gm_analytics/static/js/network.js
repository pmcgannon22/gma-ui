var w = 960,
    h = 500
    r = 10; //node radius

var color = d3.scale.category20();

var force = d3.layout.force()
.charge(-10000)
.linkDistance(325)
.gravity(.7)
.size([w, h]);

var svg = d3.select("#network").append("svg")
.attr("width", w)
.attr("height", h)
.attr("viewBox", "0 0 " + w + " " + h )
.attr("preserveAspectRatio", "xMinYMin meet");

d3.json("/group/4234424/graph", function(error, graph) {
    console.log(graph);
    force.nodes(graph.nodes)
      .links(graph.links)
      .start();

    svg.append("defs").append("marker")
      .attr("id", "arrowhead")
      .attr("refX", 1)
      .attr("viewBox", "0 0 10 10")
      .attr("refY", 5)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M 0 0 L 10 5 L 0 10 z");

  var link = svg.selectAll(".link-wrap")
      .data(graph.links)
    .enter().append("g")
      .attr("class", "link-wrap")
      .append("path")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); })
      .attr("marker-end", "url(#arrowhead)");

  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("image")
      .attr("class", "node")
      .attr("x", -r/2)
      .attr("y", -r/2)
      .attr("width", r)
      .attr("height", r)
      .on("mouseover", fade(.1)).on("mouseout", fade(1));

    var linkedByIndex = {};
    graph.links.forEach(function(d) {
      linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });

function neighboring(a, b) {
    if(linkedByIndex[a.index + "," + b.index]){
        return 1;
    } else if(linkedByIndex[b.index + "," + a.index]) {
        return -1;
    } else {
        return 0;
    }
}

function fade(opacity) {
    return function(d) {
        link.style("stroke-opacity", function(o) {
            return o.source === d || o.target === d ? 1 : opacity;
        }).style("stroke", function(o) {
            if(opacity < 1) {
                if(o.source === d) return "#FFCC6C"; //Out Edge Color
                else if(o.target === d) return "#00CDCD"; //In Edge Color
                else return "";
            }
            return "";
        }).style("stroke-width", function(o) {
            if(opacity < 1) {
                if(o.source === d || o.target === d) {
                    d3.select(this.nextSibling).style("display","block");
                    return "3px";
                }
            }
            d3.select(this.nextSibling).style("display","");
            return "";
        });

    };
}

  node.append("title")
      .text(function(d) { return d.name; });
  force.on("tick", function() {
      node.attr("cx", function(d) { return d.x = Math.max(r, Math.min(w - r, d.x)); })
          .attr("cy", function(d) { return d.y = Math.max(r, Math.min(h - r, d.y)); });

        link.attr("d", function(d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + d.source.x + "," + d.source.y + " A" + dr + "," + dr + " 0 0, 1 " +
                    d.target.x + "," + d.target.y;
        });
  });

  force.on("end", function() {
          svg.selectAll(".link-wrap").each(function(d, i) {
              var t = d3.select(this);
              var n = t.select(".link").node();
              var point = n.getPointAtLength(n.getTotalLength()/2);
              t.append("text").attr("class", "edge-weight")
                  .text(d.weight).attr("x", point.x).attr("y", point.y);
        });
  })
});
