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

const draw_updatable_text = (parent_el, text_data, update, cls=null) => {
  const el = parent_el.append("text");
  el.attr("x", text_data.x);
  el.attr("y", text_data.y);
  if(cls){
    el.attr("class", cls);
  }
  return {el: el, update: (v) => { el.text(update(v)); }};
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

  draw_text(el, {x: lpos + 0.5*w, y: h/2.0, text: mode_choice_data.label}, "mode-choice-label")
    .attr("font-size", mode_choice_data.fs);

  draw_line(el, { ends: [ [lpos + w + (lw/2.0), 0],
                          [lpos + w + (lw/2.0), h] ],
                  lw: lw }, "scaffolding");

  return { el:el, re: (i+1)*(w+lw) };
}

const add_param_trace = (parent_el, trace_data) => {

  const pd = trace_data.plot_dims;

  const i = trace_data.trace_i;
  const lpos = trace_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = trace_data.y_start;

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", "trace")
                      .attr("id", `trace-${i}`);

  el.append("text").attr("transform", `translate(${(pd.w + pd.ml)/2.0}, ${pd.mt*0.5})`)
                   .attr("text-anchor", "middle").text(trace_data.label);

  // Declare the x (horizontal position) scale.
  const xdomx = 100;
  const x = d3.scaleLinear()
      .domain([0, xdomx])
      .range([0, pd.w]);

  // Declare the y (vertical position) scale.
  const y = d3.scaleLinear()
      .domain(trace_data.yrange)
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

  if(trace_data.units.length){
    yax.append("text")
         .attr("text-anchor", "middle")
         .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`)
         .text(`[${trace_data.units}]`);
  }

  const line = d3.line()
               .x((d, i) => { return x(i); })
               .y((d, i) => { return y(d); });

  const data = [];
  const build_path = () => {
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
      const opath = build_path();
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

const add_osc_prob = (parent_el, prob_data) => {

  const pd = prob_data.plot_dims;

  const i = prob_data.prob_i;
  const lpos = prob_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = prob_data.y_start;

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", "prob")
                      .attr("id", `prob-${i}`);

  // Declare the x (horizontal position) scale.
  const x = d3.scaleLinear()
      .domain(prob_data.xrange)
      .range([0, pd.w]);

  // Declare the y (vertical position) scale.
  const y = d3.scaleLinear()
      .domain(prob_data.yrange)
      .range([pd.h, 0]);

  const xax = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${pd.ml},${pd.h+pd.mt})`)
      .call(d3.axisBottom(x).ticks(pd.nxticks))

  xax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${pd.w*0.5}, ${pd.mb*0.75})`)
       .text(`Neutrino Energy [GeV]`);

  // Add the y-axis.
  const yax = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${pd.ml},${pd.mt})`)
      .call(d3.axisLeft(y).ticks(pd.nyticks))

  yax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`)
       .text(`${prob_data.ylabel}`);

  const nu_line = d3.line()
               .x((d) => { return x(d[0]); })
               .y((d) => { return y(d[1]); });

  let nub_line = null;
  if(prob_data.dobar){
    nub_line = d3.line()
                 .x((d) => { return x(d[0]); })
                 .y((d) => { return y(d[2]); });
  }

  const data = [];
  const build_path = (line, cls) => {
    const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
    const p = pg.append("path")
        .datum(data)
        .attr("class", cls)
        .attr("d", line);
    return [pg,p];
  };
  let nu_path = build_path(nu_line, "prob-series nu");
  let nub_path = null;
  if(nub_line){
    nub_path = build_path(nub_line, "prob-series nub");
  }

  return {el:el, update: (d) => {
    data.length = 0;
    d.forEach((e)=>{data.push(e)});
    nu_path[1].attr("d", nu_line);
    if(nub_line){
      nub_path[1].attr("d", nub_line);
    }
  }};
}

const add_3flavor_triangle = (parent_el, flvtri_data) => {

  const pd = flvtri_data.plot_dims;
  pd.h = pd.w/2.0 * Math.tan(Math.PI/3.0);

  const i = flvtri_data.flvtri_i;
  const lpos = flvtri_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = flvtri_data.y_start;

  console.log(`translate(${lpos},${tpos})`);

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", "trace")
                      .attr("id", `trace-${i}`);

  // Declare the x (horizontal position) scale.
  const numu_frac_trans = d3.scaleLinear()
                    .domain([0, 1])
                    .range([0, pd.w]);

  // Declare the y right (vertical position) scale.
  const nue_frac_trans = d3.scaleLinear()
                   .domain([0,1])
                   .range([pd.w, 0]);

  // Declare the y left (vertical position) scale.
  const nutau_frac_trans = d3.scaleLinear()
                   .domain([1,0])
                   .range([pd.w, 0]);

  //x is numu content
  const xax = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${pd.ml},${pd.h+pd.mt})`)
      .call(d3.axisBottom(numu_frac_trans).ticks(pd.nxticks))

  xax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${pd.w*0.5}, ${pd.mb*0.75})`)
       .text(`numu fraction`);

  const yax_shunt = pd.ml + (pd.w/2.0);

  // Add the y-axis.
  const yaxr = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${yax_shunt},${pd.mt}),rotate(-30)`)
      .call(d3.axisRight(nue_frac_trans).ticks(pd.nyticks))

  yaxr.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${pd.ml*0.75}, ${pd.h*0.5}),rotate(-270)`)
       .text(`nue fraction`);

  const yaxl = el.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${yax_shunt},${pd.mt}),rotate(30)`)
      .call(d3.axisLeft(nutau_frac_trans).ticks(pd.nyticks))

  yaxl.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`)
       .text(`nutau fraction`);

  const cospib3 = Math.cos(Math.PI/3.0);
  const cospib6 = Math.cos(Math.PI/6.0);
  const tanpib3 = Math.tan(Math.PI/3.0);
  const sinpib3 = Math.sin(Math.PI/3.0);

  const xtrns = numu_frac_trans;
  const ytrns = d3.scaleLinear()
                   .domain([0,0.5*tanpib3])
                   .range([pd.h,0]);

  const da = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);

  draw_line(da, { ends: [ [xtrns(0),ytrns(-0.2)], [xtrns(1),ytrns(-0.2)] ], lw:1 }, "scaffolding");
  draw_line(da, { ends: [ [xtrns(0),ytrns(-0.215)], [xtrns(0),ytrns(-0.185)] ], lw:1 }, "scaffolding");

  let get_intersect = (m,c,mp,cp) => {
    const xslv = (cp - c)/(m - mp);
    const yslv = m * xslv + c;
    return [xslv, yslv];
  };

  let slvstart = get_intersect(tanpib3, 0, -tanpib3, 2*cospib6 * 0.2);
  let slvend = get_intersect(0, 0.05, -tanpib3, 2*cospib6 * 0.2);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nutau");
  slvstart = get_intersect(tanpib3, 0, -tanpib3, 2*cospib6 * 0.4);
  slvend = get_intersect(0, 0.05, -tanpib3, 2*cospib6 * 0.4);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nutau");
  slvstart = get_intersect(tanpib3, 0, -tanpib3, 2*cospib6 * 0.6);
  slvend = get_intersect(0, 0.05, -tanpib3, 2*cospib6 * 0.6);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nutau");
  slvstart = get_intersect(tanpib3, 0, -tanpib3, 2*cospib6 * 0.8);
  slvend = get_intersect(0, 0.05, -tanpib3, 2*cospib6 * 0.8);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nutau");

  slvstart = get_intersect(0, 0, tanpib3, -tanpib3 * 0.2);
  slvend = get_intersect(-tanpib3,1.9*cospib6, tanpib3, -tanpib3 * 0.2);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding");
  slvstart = get_intersect(0, 0, tanpib3, -tanpib3 * 0.4);
  slvend = get_intersect(-tanpib3,1.9*cospib6, tanpib3, -tanpib3 * 0.4);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding");
  slvstart = get_intersect(0, 0, tanpib3, -tanpib3 * 0.6);
  slvend = get_intersect(-tanpib3,1.9*cospib6, tanpib3, -tanpib3 * 0.6);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding");
  slvstart = get_intersect(0, 0, tanpib3, -tanpib3 * 0.8);
  slvend = get_intersect(-tanpib3,1.9*cospib6, tanpib3, -tanpib3 * 0.8);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding");

  slvstart = get_intersect(tanpib3, -0.1, 0, sinpib3 * 0.2);
  slvend = get_intersect(-tanpib3, 2*cospib6, 0, sinpib3 * 0.2);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nue");
  slvstart = get_intersect(tanpib3, -0.1, 0, sinpib3 * 0.4);
  slvend = get_intersect(-tanpib3, 2*cospib6, 0, sinpib3 * 0.4);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nue");
  slvstart = get_intersect(tanpib3, -0.1, 0, sinpib3 * 0.6);
  slvend = get_intersect(-tanpib3, 2*cospib6, 0, sinpib3 * 0.6);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nue");
  slvstart = get_intersect(tanpib3, -0.1, 0, sinpib3 * 0.8);
  slvend = get_intersect(-tanpib3, 2*cospib6, 0, sinpib3 * 0.8);
  draw_line(da, { ends: [ [xtrns(slvstart[0]),ytrns(slvstart[1])], [xtrns(slvend[0]),ytrns(slvend[1])] ], lw:1 }, "scaffolding nue");


  let sa = da.append("g");

  let travelel = draw_updatable_text(da, {x: xtrns(0.25), y: ytrns(-0.3)}, (v) => { return `numu travel [km]: ${v}`; }, "travel_counter")
  let travel_L_km = 0;
  let lprobs = { "prob":null, "probbar":null };

  let add_point = (d, cls) => {

    const c = -tanpib3 * d.frac_numu;
    const cp = 2*cospib6 * (d.frac_nue + d.frac_numu);

    const slv = get_intersect(tanpib3, c, -tanpib3, cp);

    const xv = xtrns(slv[0]);
    const yv = ytrns(slv[1]);

    sa.append("path")
      .attr("class", `flvtripoint ${cls}`)
      .attr("transform", `translate(${xv},${yv})`)
      .attr("d", d3.symbol(d.symbol,d.ssize)).transition().duration(d.livetime).style("opacity",0).remove();
  };

  return {el:el, update: (d, L_max) => {

    if((travel_L_km > 0) && (travel_L_km > d.L)){ // server has started neutrino again
      let point_data = { "frac_nue": lprobs.prob[0][0],
                         "frac_numu": lprobs.prob[0][1],
                         "livetime": 10000,
                         "symbol": d3.symbolWye,
                         "ssize": 30 };

      add_point(point_data, "nue");

      point_data.frac_nue = lprobs.probbar[0][0];
      point_data.frac_numu = lprobs.probbar[0][1];
      add_point(point_data, "nueb");

      point_data.frac_nue = lprobs.prob[1][0];
      point_data.frac_numu = lprobs.prob[1][1];
      add_point(point_data, "numu");

      point_data.frac_nue = lprobs.prob[2][0];
      point_data.frac_numu = lprobs.prob[2][1];
      add_point(point_data, "nutau");

      const pipx = xtrns(1);
      const pipy = ytrns(-0.2);
      sa.append("path")
        .attr("class", `flvtripoint numu`)
        .attr("transform", `translate(${pipx},${pipy})`)
        .attr("d", d3.symbol(d3.symbolWye,40)).transition().duration(10000).style("opacity",0).remove();
    }

    lprobs.prob = d.prob;
    lprobs.probbar = d.probbar;
    travel_L_km = d.L;

    travelel.update(`${travel_L_km}`);

    let point_data = {
              "frac_nue": lprobs.prob[0][0],
              "frac_numu": lprobs.prob[0][1],
              "livetime": 1000,
              "symbol": d3.symbolCircle,
              "ssize": 10 };


    add_point(point_data, "nue");

    point_data.frac_nue = lprobs.probbar[0][0];
    point_data.frac_numu = lprobs.probbar[0][1];
    add_point(point_data, "nueb");

    point_data.frac_nue = lprobs.prob[1][0];
    point_data.frac_numu = lprobs.prob[1][1];
    add_point(point_data, "numu");

    point_data.frac_nue = lprobs.prob[2][0];
    point_data.frac_numu = lprobs.prob[2][1];
    add_point(point_data, "nutau");

    const opacity_trans = (p) => {
      // return 1 - ((Math.log(1.1 - p) + 1)/(Math.log(1.1) - Math.log(0.1)));
      // return (Math.exp(p)/(Math.exp(1) - Math.exp(0))) - 1;
      return p;
    };

    const pipx = xtrns(travel_L_km/L_max);
    let pipy = ytrns(-0.185);
    sa.append("path")
      .attr("class", `flvtripoint nue`)
      .attr("transform", `translate(${pipx},${pipy})`)
      .attr("opacity", opacity_trans(lprobs.prob[1][0]))
      .attr("d", d3.symbol(d3.symbolCircle,10)).transition().duration(500).style("opacity",0).remove();

    pipy = ytrns(-0.2);
    sa.append("path")
      .attr("class", `flvtripoint numu`)
      .attr("transform", `translate(${pipx},${pipy})`)
      .attr("opacity", opacity_trans(lprobs.prob[1][1]))
      .attr("d", d3.symbol(d3.symbolCircle,10)).transition().duration(500).style("opacity",0).remove();

    pipy = ytrns(-0.215);
    sa.append("path")
      .attr("class", `flvtripoint nutau`)
      .attr("transform", `translate(${pipx},${pipy})`)
      .attr("opacity", opacity_trans(lprobs.prob[1][2]))
      .attr("d", d3.symbol(d3.symbolCircle,10)).transition().duration(500).style("opacity",0).remove();
  }};

}

const build_ui = (cfg) => {

  const scaff =  cfg.ui.scaffolding;

  const page_w = scaff.page.w;
  const page_h = scaff.page.h;

  const svg = d3.create("svg")
      .attr("width", page_w)
      .attr("height", page_h);

  const mode_choices = [];
  cfg.controls.modes.forEach((m, i)=>{
    mode_choices.push(add_mode_choice(svg, {i: i, label: m.label,
      w: scaff.mode_select.w, h: scaff.mode_select.h, lw: scaff.line.w,
      fs: scaff.mode_select.fs }));
  });

  const scaff_el = svg.append("g").attr("class", "scaffolding");

  let hline_height = scaff.mode_select.h + 2;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");
  hline_height += 2;

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
                                        units: cfg.controls.parameters[param_i].units,
                                        yrange: cfg.controls.parameters[param_i].range,
                                        x_start : 0,
                                        y_start: hline_height,
                                        plot_dims: scaff.plots.trace}));
    }
  });

  hline_height += 2 + scaff.plots.trace.mt + scaff.plots.trace.h + scaff.plots.trace.mb;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");
  hline_height += 2;

  const mode_choice_re = mode_choices[mode_choices.length-1].re;
  const top_right_text = svg.append("g").attr("transform", `translate(${mode_choice_re}, 10)`);

  const text_elements = [];
  text_elements.push(draw_updatable_text(top_right_text, {x: 10, y: 10}, (v) => { return `uptime [ticks]: ${v}`; }, "ticker"));
  text_elements.push(draw_updatable_text(top_right_text, {x: 225, y: 10}, (v) => { return `baseline [km]: ${v}`; }, "ticker"));

  const osc_probability = [];
  cfg.ui.plots.osc_probability.forEach((m, i) => {
    osc_probability.push(add_osc_prob(svg, {prob_i: osc_probability.length,
                                      ylabel: m.ylabel,
                                      xrange: m.xrange,
                                      yrange: m.yrange,
                                      x_start : 0,
                                      y_start: hline_height,
                                      dobar: m.dobar,
                                      plot_dims: scaff.plots.osc_probability}));

  });

  hline_height += 2 + scaff.plots.osc_probability.mt + scaff.plots.osc_probability.h + scaff.plots.osc_probability.mb;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");
  hline_height += 2;

  const flvtriangles = [];
  cfg.ui.plots.flvtriangles.forEach((m, i) => {
    flvtriangles.push(add_3flavor_triangle(svg, {flvtri_i: flvtriangles.length,
                                      x_start : 0,
                                      y_start: hline_height,
                                      plot_dims: scaff.plots.flvtriangles}));

  });

  // Append the SVG element.
  container.append(svg.node());

  return { traces: traces,
           text_elements: text_elements,
           osc_probability: osc_probability,
           flvtriangles: flvtriangles };
}

const websocket = new WebSocket("ws://localhost:5678/");

let ui_els = null;
let trace_param = [];

let once = true;

websocket.onmessage = ({data}) => {
  const obj = JSON.parse(data);
  // console.log(obj);

  if (obj.cmd == "ui_start"){
    console.log("Building UI");
    ui_els = build_ui(obj.cfg.noec);
  } else if(obj.cmd == "UPDATE"){
    // console.log(obj);
    // ui_els.traces.forEach( (m, i) => { m.update(obj.vals[m.param_i]); } );
    // ui_els.text_elements[0].update(obj.tick);
    // ui_els.text_elements[1].update(obj.L_km);
    // ui_els.osc_probability[0].update(obj.osc_probs.numu);
    // ui_els.osc_probability[1].update(obj.osc_probs.nue);
    // if(once){
      ui_els.flvtriangles[0].update(obj.trans_prob_max, obj.L_km);
    //   once = false;
    // }
  }
};
