const draw_line = (parent_el, line_data, cls=null) => {
  const line = d3.line();
  const el = parent_el.append("path")
    .attr("d", line(line_data.ends))
    .style("stroke-width", line_data.lw);
  if(cls){
    el.attr("class", cls);
  }
  return el;
}

const draw_rect = (parent_el, rect_data, cls=null) => {
  const path = d3.path();
  path.rect(rect_data.x, rect_data.y, rect_data.w, rect_data.h);
  const el = parent_el.append("path")
    .attr("d", path.toString());
  if(cls){
    el.attr("class", cls);
  }
  return el;
}

const draw_text = (parent_el, text_data, cls=null) => {
  const el = parent_el.append("text");
  el.attr("x", text_data.x);
  el.attr("y", text_data.y);
  el.text(text_data.text);
  if(cls){
    el.attr("class", cls);
  }
  return el;
}

const add_mode_choice = (parent_el, mode_choice_data) => {
  const i = mode_choice_data.i;
  const w = mode_choice_data.w;
  const h = mode_choice_data.h;
  const lw = mode_choice_data.lw;

  const el = parent_el.append("g").attr("id",`mode-choice-${i}`)
                                               .attr("class","ui mode-choice");

  const lpos = i*(w+lw);
  draw_rect(el, {x:lpos, y:0, w:w, h:h},"mode-choice-bkg");

  draw_text(el, {x: lpos + 0.5*w, y: h/2.0, text: mode_choice_data.label}, "mode-choice-label");

  draw_line(el, { ends: [ [lpos + w + (lw/2.0), 0],
                          [lpos + w + (lw/2.0), h] ],
                  lw: lw }, "scaffolding");

  return el;
}

const add_param_trace = (parent_el, trace_data) => {

  const pd = trace_data.plot_dims;

  const i = trace_data.trace_i;
  const lpos = pd.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = pd.y_start;

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", "trace")
                      .attr("id", `trace-${i}`);

  el.append("text").attr("transform", `translate(${(pd.w + pd.ml)/2.0}, ${pd.mt*0.5})`).attr("text-anchor", "middle").text(trace_data.label);

  // Declare the x (horizontal position) scale.
  const xdomx = 100;
  const x = d3.scaleLinear()
      .domain([0, xdomx])
      .range([0, pd.w]);

  // Declare the y (vertical position) scale.
  const y = d3.scaleLinear()
      .domain([0, 255])
      .range([pd.h, 0]);

  // Add the y-axis.
  const yax = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${pd.ml},${pd.mt})`)
      .call(d3.axisLeft(y).ticks(pd.nyticks))
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line").clone()
                  .attr("x2", pd.w)
                  .attr("stroke-opacity", 0.15));
  yax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`).text("ADC");

  let line = d3.line()
               .x((d, i) => { return x(i); })
               .y((d, i) => { return y(d); });

  let data = [];
  let build_path = () => {
    const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
    const p = pg.append("path")
        .datum(data)
        .attr("class", "trace-series")
        .attr("d", line);
    return [pg,p];
  };
  let path = build_path();

  return {el:el, param_i: trace_data.param_i, update: (d) => {
    if(data.length >= xdomx){
      let opath = build_path();
      opath[0].transition().duration(1000).style("opacity",0).remove();

      data.length = 0;
      data.push(d);
      path[0].remove();
      path = build_path();
    } else {
      data.push(d);
    }

    path[1].attr("d", line);
  }};
}

const build_ui = (cfg) => {

  const scaff =  cfg.ui.scaffolding;

  const page_w = scaff.page.w;
  const page_h = scaff.page.h;

  const svg = d3.create("svg")
      .attr("width", page_w)
      .attr("height", page_h);

  const mode_select_w = scaff.mode_select.w;
  const mode_select_h = scaff.mode_select.h;

  const line_w = scaff.line.w;

  cfg.controls.modes.forEach((m, i)=>{
    add_mode_choice(svg, {i: i, label: m.label, w: mode_select_w, h: mode_select_h, lw: line_w});
  });

  const scaff_el = svg.append("g").attr("class", "scaffolding");

  draw_line(scaff_el, { ends: [ [0, mode_select_h], [page_w, mode_select_h] ], lw:4 }, "scaffolding");

  draw_line(scaff_el, { ends: [ [0, mode_select_h], [page_w, mode_select_h] ], lw:4 }, "scaffolding");

  const traces = [];

  cfg.ui.plots.traces.forEach((m, i) => {

    let param_i = null;
    for (var par_it = 0; par_it < cfg.controls.parameters.length; par_it++) {
      if (cfg.controls.parameters[par_it].name == m.parameter){
        param_i = par_it;
      }
    }

    if(param_i == null){
      console.log(`Trace requested for parameter ${m.parameter} that could not be found`);
    } else {
      traces.push(add_param_trace(svg, {trace_i: traces.length,
                                        param_i: param_i,
                                        label: m.parameter,
                                        plot_dims: scaff.plots.trace}));
    }
  });

  // Append the SVG element.
  container.append(svg.node());

  return {traces: traces};
}

const websocket = new WebSocket("ws://localhost:5678/");

let ui_els = null;
let trace_param = [];

websocket.onmessage = ({data}) => {
  const obj = JSON.parse(data);
  // console.log(obj);

  if (obj.cmd == "ui_start"){
    console.log("Building UI");
    ui_els = build_ui(obj.cfg.noec);
  } else if(obj.cmd == "UPDATE"){
    ui_els.traces.forEach( (m, i) => { m.update(obj.vals[m.param_i]); } );
  }
};
