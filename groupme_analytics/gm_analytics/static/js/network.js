var w = 960,
    h = 500
    r = 10; //node radius

var color = d3.scale.category20();

var force = d3.layout.force()
    .charge(function(d) { return d.weight; })
//    .linkDistance(325)
    .gravity(0)
    .size([w, h]);

var zones = [5, 2]; //[horizontal,vertical] division
var foci = [];
for(var a=1;a<=zones[0];a++) {
    for(var b=1;b<=zones[1];b++) {
        var xf = ((w/zones[0])*(2*a - 1))/2;
        var yf = ((h/zones[1])*(2*b-1))/2;
        foci.push({x: xf, y: yf});
    }
}

var svg = d3.select("#network").append("svg")
.attr("width", w)
.attr("height", h)
.attr("viewBox", "0 0 " + w + " " + h )
.attr("preserveAspectRatio", "xMinYMin meet");

d3.json("/group/4234424/graph", function(error, graph) {
    force.nodes(graph.nodes)
      .links(graph.links);

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

  force.on("tick", function(e) {
      var k = ~~(100  * Math.random());

  // Push nodes toward their designated focus.
      graph.nodes.forEach(function(o, i) {
        var foc  = parseInt(o.id) % (zones[0] * zones[1]);

        var yy = (Math.random() < 0.5 ? -1 : 1) * k + foci[foc].y;
        var xx = (Math.random() < 0.5 ? -1 : 1) * k + foci[foc].x;
        if(xx > r && xx < (w-r))
            o.x = xx;
        if(yy > r && yy < (h-r))
            o.y = yy;
      });
  });

  var link, node;
  setTimeout(function() {
        force.start();
        for (var i = 100; i > 0; --i) force.tick();
        force.stop();

        link = svg.selectAll(".link-wrap")
            .data(graph.links)
            .enter().append("g")
            .attr("class", "link-wrap")
            .append("path")
            .attr("class", "link")
            .style("stroke-width", function(d) { return Math.sqrt(d.value); })
            .attr("marker-end", "url(#arrowhead)");

        node = svg.selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")
            .attr("class", "node")
            .on("mouseover", fade(.1)).on("mouseout", fade(1));

        graph.nodes.forEach(function(d, i) {
          svg.select("defs").append("pattern")
              .attr("id", "image-" + d.id)
              .attr("x", 0).attr("y",0)
              .attr("height", 40).attr("width", 40)
              .append("image")
              .attr("x",0).attr("y",0)
              .attr("height", 40).attr("width", 40)
              .attr("xlink:href", d.img);
        });
        node.append("circle")
            .attr("xlink:href", function(d) { console.log(d); return d.img; })
            .attr("class", "img-clip")
            .attr("cx", 0)
            .attr("cy", 0)
            .attr("r", 20)
            .attr("title", function(d) { return d.name; });

        node.attr("transform", function(d) { return "translate(" + Math.max(r, Math.min(w - r, d.x))
                                                      + "," + Math.max(r, Math.min(h - r, d.y)) + ")"; });
        link.attr("d", function(d) {
          var dx = d.target.x - d.source.x,
              dy = d.target.y - d.source.y,
              dr = Math.sqrt(dx * dx + dy * dy);
          return "M" + d.source.x + "," + d.source.y + " A" + dr + "," + dr + " 0 0, 1 " +
                  d.target.x + "," + d.target.y;
        });

        svg.selectAll(".link-wrap").each(function(d, i) {
              var t = d3.select(this);
              var n = t.select(".link").node();
              var point = n.getPointAtLength(n.getTotalLength()/2);
              t.append("text").attr("class", "edge-weight")
                  .text(d.weight).attr("x", point.x).attr("y", point.y);
        });

        svg.selectAll(".img-clip")
            .attr("fill", function(d) { return "url(#image-" + d.id + ")"; });
        $("svg circle.img-clip").tooltip({
            'container': 'body',
            'placement': 'top'
        });

  }, 50);


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

          var img_size = 15;
          //resize image??
      };
  }
});
