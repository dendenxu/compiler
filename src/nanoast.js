// ************** Generate the tree diagram	 *****************
const BASE_WIDTH = 1900;
const BASE_HEIGHT = 820;
var margin = {
    top: 20,
    right: 120,
    bottom: 20,
    left: 120,
  },
  width = BASE_WIDTH - margin.right - margin.left,
  height = BASE_HEIGHT - margin.top - margin.bottom;

var i = 0,
  duration = 750,
  root;

var tree = d3.layout.tree().size([height, width]);

var diagonal = d3.svg.diagonal().projection(function (d) {
  return [d.y, d.x];
});

var svgelement = d3
  .select("body")
  .append("svg")
  .attr("width", width + margin.right + margin.left)
  .attr("height", height + margin.top + margin.bottom);

var svg = svgelement
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

const dataFile = "./tree.json";
var approx_width = BASE_WIDTH;
var approx_height = BASE_HEIGHT;
d3.json(dataFile, (payload) => {
  console.log(`Loaded data from local file: ${dataFile}`);
  root = payload;

  if (root.size) {
    approx_width = root.size[0];
    approx_height = root.size[1];

    console.log(`Loaded width: ${approx_width}, height: ${approx_height}`);
    if (root.children) updateWH(approx_width, approx_height);
  }

  root.x0 = height / 2;
  root.y0 = 0;
  update(root);
  d3.select(self.frameElement).style("height", "500px");
  document.title = root.filename;
  titlenode = document.getElementById("bigtitle");
  titlenode.innerText += ": ";
  // titlenode.setAttribute("")
  // .appendChild(`<strong>${}</strong>`)
  filenamenode = document.createElement("strong");
  filenamenode.innerText = document.title;
  titlenode.appendChild(filenamenode);

  if (root.address) {
    addrnode = document.createElement("h2");
    addrnode.innerText = root.address;
    centernode = document.getElementById("centernode");
    centernode.appendChild(addrnode);
  }
});

const updateWH = (width, height) => {
  tree_width = width - margin.right - margin.left;
  tree_height = height - margin.top - margin.bottom;
  ori_height = tree.size()[0]; // the first element is the height

  console.log(`Tree width: ${tree_width}, height: ${tree_height}`);

  tree.size([tree_height, tree_width]);

  if (tree_height < ori_height) {
    setTimeout(() => {
      svgelement.attr("width", width).attr("height", height);
    }, duration);
  } else {
    svgelement.attr("width", width).attr("height", height);
  }
};

function update(source) {
  // const dx = 0;
  const dx = -16;
  const enddx = 16;
  // const dy = -16;
  const dy = "0.35em";
  const enddy = "0.35em";
  const anchorinner = "end";
  const anchorleaf = "start";
  const eps = 1e-6;
  const width = 180;
  const radius = 10;
  const big_radius = 12;
  const opacity = 1;
  const larger_node_desc = ["Func", "Block", "Prog"];
  const judge = (data) => {
    // console.log(data)
    // console.log(larger_node_desc)
    if (data.name) {
      return larger_node_desc.some((e) => data.name.includes(e));
    } else {
      return false;
    }
  };
  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
    links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function (d) {
    d.y = d.depth * width;
  });

  // Update the nodes???
  var node = svg.selectAll("g.node").data(nodes, function (d) {
    return d.id || (d.id = ++i);
  });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", function (d) {
      return "translate(" + source.y0 + "," + source.x0 + ")";
    })
    .on("click", click);

  nodeEnter
    .append("circle")
    .attr("r", eps)
    .style("fill", function (d) {
      return d._children ? "lightsteelblue" : "#fff";
    })
    .style("stroke", function (d) {
      return judge(d) ? "#ff99a8" : "steelblue";
    });

  nodeEnter
    .append("text")
    .attr("x", function (d) {
      return d.children || d._children ? dx : enddx;
    })
    .attr("dy", (d) => {
      return d.children || d._children ? dy : enddy;
    })
    .attr("text-anchor", function (d) {
      return d.children || d._children ? anchorinner : anchorleaf;
    })
    .text(function (d) {
      return d.name;
    })
    .style("fill-opacity", eps);

  // Transition nodes to their new position.
  var nodeUpdate = node
    .transition()
    .duration(duration)
    .attr("transform", function (d) {
      return "translate(" + d.y + "," + d.x + ")";
    });

  nodeUpdate
    .select("circle")
    .attr("r", (d) => {
      return judge(d) ? big_radius : radius;
    })
    .style("fill-opacity", opacity)
    .style("fill", function (d) {
      if (d._children) {
        return judge(d) ? "#eebbc4" : "lightsteelblue";
      } else {
        return judge(d) ? "#44000f" : "#222";
      }
    });

  nodeUpdate
    .select("text")
    .style("fill-opacity", opacity)
    .style("font-weight", (d) => {
      return judge(d) ? "600" : "400";
    });

  // Transition exiting nodes to the parent's new position.
  var nodeExit = node
    .exit()
    .transition()
    .duration(duration)
    .attr("transform", function (d) {
      return "translate(" + source.y + "," + source.x + ")";
    })
    .remove();

  nodeExit.select("circle").attr("r", eps);

  nodeExit.select("text").style("fill-opacity", eps);

  // Update the links???
  var link = svg.selectAll("path.link").data(links, function (d) {
    return d.target.id;
  });

  // Enter any new links at the parent's previous position.
  link
    .enter()
    .insert("path", "g")
    .style("stroke-width", (d) => {
      // console.log(d)
      if (d.source && d.target && judge(d.source) && judge(d.target)) {
        return "5px";
      } else {
        return "2px";
      }
    })
    .style("stroke", (d) => {
      if (d.source && d.target && judge(d.source) && judge(d.target)) {
        return "#eee";
      } else {
        return "#aaa";
      }
    })
    .attr("class", "link")
    .attr("d", function (d) {
      var o = {
        x: source.x0,
        y: source.y0,
      };
      return diagonal({
        source: o,
        target: o,
      });
    });

  // Transition links to their new position.
  link.transition().duration(duration).attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link
    .exit()
    .transition()
    .duration(duration)
    .attr("d", function (d) {
      var o = {
        x: source.x,
        y: source.y,
      };
      return diagonal({
        source: o,
        target: o,
      });
    })
    .remove();

  // Stash the old positions for transition.
  nodes.forEach(function (d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}

const expandall = (node) => {
  if (node._children) {
    node.children = node._children;
    node._children = null;
  }
  if ((nodes = node.children)) {
    nodes.forEach((node) => {
      expandall(node);
    });
  }
};

const collapseall = (node) => {
  if (node.children) {
    node._children = node.children;
    node.children = null;
  }
  if ((nodes = node._children)) {
    nodes.forEach((node) => {
      collapseall(node);
    });
  }
};

const expand = window.document.getElementById("expand");
const collapse = window.document.getElementById("collapse");
const grow = window.document.getElementById("grow");
const shrink = window.document.getElementById("shrink");
const download = window.document.getElementById("downloadsvg");

expand.addEventListener("click", () => {
  updateWH(approx_width, approx_height);
  expandall(root);
  update(root);
});

collapse.addEventListener("click", () => {
  updateWH(BASE_WIDTH, BASE_HEIGHT);
  collapseall(root);
  root.x0 = BASE_HEIGHT / 2;
  root.y0 = 0;
  update(root);
});

grow.addEventListener("click", () => {
  width = svgelement.attr("width");
  height = svgelement.attr("height");
  updateWH(width * 2, height * 2);
  update(root);
});

shrink.addEventListener("click", () => {
  width = svgelement.attr("width");
  height = svgelement.attr("height");
  console.log("Shrinking");
  console.log(height / 2);
  console.log(BASE_HEIGHT);
  updateWH(Math.max(width / 2, BASE_WIDTH), Math.max(height / 2, BASE_HEIGHT));
  update(root);
});

download.addEventListener("click", async () => {
  console.log(svgelement[0][0]);
  todownload = svgelement[0][0].cloneNode(true);

  content = await $.get("./nanoast.css");
  style = $("<style>").html(content)[0];
  console.log(style);
  // console.log(style.outerHTML);

  todownload.insertBefore(style, todownload.firstChild);
  todownload.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  todownload.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");

  console.log(todownload);

  //convert svg source to URI data scheme.
  var svgData = todownload.outerHTML;

  console.log(svgData);

  var svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  var svgUrl = URL.createObjectURL(svgBlob);
  var downloadLink = document.createElement("a");
  downloadLink.href = svgUrl;
  downloadLink.download = "nanoast.svg";
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
});
