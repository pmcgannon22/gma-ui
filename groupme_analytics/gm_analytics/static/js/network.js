
//group id set at top of group.html template
d3.json("/group/" + group_id + "/graph", function(error, graph) {
    var w = 3400,
        h = 2000,
        elemWidth = 1100,
        elemHeight = 525,
        r = 30,
        color = d3.scale.category20();

    var max_weight = d3.max(graph.links, function(d) { return d.weight; });
    var linkWeights = [];
    graph.links.forEach(function(e, i, arr) {
        linkWeights[e.source] = linkWeights[e.source] || [];
        linkWeights[e.target] = linkWeights[e.target] || [];
        if(linkWeights[e.target][e.source] == undefined) {
            linkWeights[e.source][e.target] =  e.weight;
        } else {
            linkWeights[e.source][e.target] =  Math.sqrt(e.weight * linkWeights[e.target][e.source]);
            linkWeights[e.target][e.target] = linkWeights[e.source][e.target];
        }
    });

    var force = d3.layout.force()
        .charge(function(d) { return -500; })
        .linkDistance(function(a) {
            return ((max_weight + 1 - linkWeights[a.source.index][a.target.index])/max_weight) * (w/2.5);
         })
        .size([w, h]);

    force.nodes(graph.nodes)
      .links(graph.links);

    var svgWrap = d3.select("#network").append("svg")
    .attr("width", elemWidth)
    .attr("height", elemHeight);

    var viewBoxCoords = {x1: 0, y1: 0, x2: w, y2: h};

    var svg = svgWrap.append("svg")
        .attr("y", "25px")
        .attr("width", elemWidth)
        .attr("viewBox", viewBoxCoords.x1 + " " + viewBoxCoords.y1 + " " + viewBoxCoords.x2 + " " + viewBoxCoords.y2)
        .attr("preserveAspectRatio", "xMidYMin meet");


    function zoom(direction) {
        //todo: fix zoom in too far
        var zoomFactor = .2;
        var n = direction === 'in' ? -1 : 1;
        var dx = ~~((viewBoxCoords.x2 - viewBoxCoords.x1) * zoomFactor);
        var dy = ~~((viewBoxCoords.y2 - viewBoxCoords.y1) * zoomFactor);
        dx = dx > 50 ? dx : 50;
        dy = dy > 50 ? dy : 50;
        viewBoxCoords.x1 = viewBoxCoords.x1 - n * dx > 0 ? viewBoxCoords.x1 - n * dx : viewBoxCoords.x1;
        viewBoxCoords.x2 = viewBoxCoords.x2 + n * dx < w && viewBoxCoords.x2 + n * dx > 0 ? viewBoxCoords.x2 + n * dx : 75;
        viewBoxCoords.y1 = viewBoxCoords.y1 - n * dy > 0 ? viewBoxCoords.y1 - n * dy : viewBoxCoords.y1;
        viewBoxCoords.y2 = viewBoxCoords.y2 + n * dy < h && viewBoxCoords.y2 + n * dy > 0 ? viewBoxCoords.y2 + n * dy : 75;
    }

    svgWrap.append("text")
        .text("+")
        .attr("class", "zoom in")
        .attr("x", elemWidth - 25).attr("y",15)
        .on("click", function() {
            zoom('in');
            svg.attr("viewBox", viewBoxCoords.x1 + " " + viewBoxCoords.y1 + " " + viewBoxCoords.x2 + " " + viewBoxCoords.y2);
        });

    svgWrap.append("text")
        .text("–")
        .attr("class", "zoom out")
        .attr("x", elemWidth - 24).attr("y",30)
        .on("click", function() {
            zoom('out');
            svg.attr("viewBox", viewBoxCoords.x1 + " " + viewBoxCoords.y1 + " " + viewBoxCoords.x2 + " " + viewBoxCoords.y2);
        });
    var drag = d3.behavior.drag()
        .on("drag", dragmove)
        .on("dragstart", function() {
            $(this).css('cursor', 'move');
        }).on("dragend", function() {
            $(this).css('cursor', '');
        });

    function dragmove() {
        viewBoxCoords.x1 -= d3.event.dx;
        viewBoxCoords.y1 -= d3.event.dy
        svg.attr("viewBox", viewBoxCoords.x1 + " " + viewBoxCoords.y1 + " " + viewBoxCoords.x2 + " " + viewBoxCoords.y2);
    }
    svgWrap.call(drag);

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

    force.start();

    var link = svg.selectAll(".link-wrap")
        .data(graph.links)
        .enter().append("g")
        .attr("class", "link-wrap")
        .append("path")
        .style("display", function(d) { console.log(d); return "";})
        .attr("class", "link")
        .style("stroke-width", function(d) { return Math.sqrt(d.value); });
        //.attr("marker-end", "url(#arrowhead)");

    var node = svg.selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .on("mouseover", fade(.1)).on("mouseout", fade(1));

    graph.nodes.forEach(function(d, i) {
      svg.select("defs").append("pattern")
          .attr("id", "image-" + d.id)
          .attr("x", 0).attr("y",0)
          .attr("height", 2*r).attr("width", 2*r)
          .append("image")
          .attr("x",0).attr("y",0)
          .attr("height", 2*r).attr("width", 2*r)
          .attr("xlink:href", d.img);
    });
    node.append("circle")
        .attr("xlink:href", function(d) { return d.img; })
        .attr("class", "img-clip")
        .attr("r", r)
        .attr("title", function(d) { return d.name; });

    force.on("tick", function() {
        link.attr("d", function(d) {
          var dx = d.target.x - d.source.x,
              dy = d.target.y - d.source.y,
              dr = Math.sqrt(dx * dx + dy * dy);
          return "M" + d.source.x + "," + d.source.y + " A" + dr + "," + dr + " 0 0, 1 " +
                  d.target.x + "," + d.target.y;
        });

        node.selectAll('circle').attr("cx", function(d) { return d.x = Math.max(r, Math.min(w - r, d.x)); })
            .attr("cy", function(d) { return d.y = Math.max(r, Math.min(h - r, d.y)); });
    });

    force.on("end", function() {
        svg.selectAll(".link-wrap").each(function(d, i) {
              var t = d3.select(this);
              var n = t.select(".link").node();
              var point = n.getPointAtLength(n.getTotalLength()/2);
              t.append("text").attr("class", "edge-weight")
                  .text(d.weight).attr("x", point.x).attr("y", point.y);
        });

        svg.selectAll(".img-clip")
            .attr("fill", function(d) { return "url(#image-" + d.id + ")"; });

        var startBoxX = d3.extent(graph.nodes, function(n) { return n.x; });
        var startBoxY = d3.extent(graph.nodes, function(n) { return n.y; });
        var xWidth = (startBoxX[1] - startBoxX[0]);
        viewBoxCoords = {x1: startBoxX[0], x2: xWidth + 4*r, y1: startBoxY[0] - 4 * r, y2: (startBoxY[1] - startBoxY[0] + 8*r)};
        svg.attr("viewBox", viewBoxCoords.x1 + " " + viewBoxCoords.y1 + " " + viewBoxCoords.x2 + " " + viewBoxCoords.y2);
        $("svg circle.img-clip").tooltip({
            'container': 'body',
            'placement': 'top'
        });
    });


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

          node.style("fill-opacity", function(o) {
              if(opacity < 1)
                  return o === d  ? 1 : .45;
              else
                  return 1;
          });
      };
  }
});
