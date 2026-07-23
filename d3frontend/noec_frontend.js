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

const draw_updateable_circle = (parent_el, circ_data, cls=null) => {
  const el = parent_el.append("circle");
  el.attr('cx', circ_data.x);
  el.attr('cy', circ_data.y);
  el.attr('r', circ_data.r);
  el.style("fill", "black");
  if(cls){
    el.attr("class", cls);
  }
  return {el: el, update: (v) => { if(v){el.style("fill", circ_data.color)}else{el.style("fill", "black");}}};
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
                      .attr("class",trace_data.cls +  "trace")
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
      .attr("class",trace_data.cls +  "axis")
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
        .attr("class",trace_data.cls +  "trace-series")
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

const add_param_map = (parent_el, param_data) => {
  const pd = param_data.plot_dims;

  const i = param_data.lh_i;
  const lpos = param_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = param_data.y_start;

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", param_data.cls)
        .attr("id", param_data.cls + `-${i}`);

  // Declare the x (horizontal position) scale.
  const x = d3.scaleLinear()
      .domain(param_data.xrange)
      .range([0, pd.w]);

  // Declare the y (vertical position) scale.
  const y = d3.scaleLinear()
      .domain(param_data.yrange)
      .range([pd.h, 0]);

  const xax = el.append("g")
      .attr("class", param_data.axiscls + "axis")
      .attr("transform", `translate(${pd.ml},${pd.h+pd.mt})`)
      .call(d3.axisBottom(x).ticks(pd.nxticks))

  xax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${pd.w*0.5}, ${pd.mb*0.75})`)
       .text(`${param_data.xlabel}`);

  // Add the y-axis.
  const yax = el.append("g")
      .attr("class", param_data.axiscls + "axis")
      .attr("transform", `translate(${pd.ml},${pd.mt})`)
      .call(d3.axisLeft(y).ticks(pd.nyticks))

  yax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`)
    .text(`${param_data.ylabel}`);

  return {el:el, pd:pd, x:x, y:y};
}

const add_two_d_lh = (parent_el, lh_data) => {
  const plot = add_param_map(parent_el, lh_data);
  const el = plot.el;
  const pd = plot.pd
  const x = plot.x;
  const y = plot.y;

  const lh_color = d3.interpolateHsl("red", "lime") 
  const data = [];
  const points = []
  const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
  for (let i =0; i<1000; i++) {
    points.push(pg.append("circle")
        .attr("r", 1)
          .attr("cx",x(0))
          .attr("cy", y(0))  
                .attr("fill", "black"));
  }
  const add_point = () => {
    let numPoints = data.slice(-1000).length
    data.slice(-1000).forEach((m, i) => {
      points[i].attr("r", 2)
          .attr("cx",x(m[0]))
          .attr("cy", y(m[1]))  
        .attr("fill", lh_color(m[2]/100))
        .attr("fill-opacity", (i+1)/numPoints)
        .attr("class","")
    })
  };
  return {el:el, update: (d) => {
    data.push(d);
    add_point();
  }}
  
}

const add_ml_walker = (parent_el, walker_data) => {
  const num_walkers = walker_data.num_walkers;
  const plot = add_param_map(parent_el, walker_data);
  const el = plot.el;
  const pd = plot.pd
  const x = plot.x;
  const y = plot.y;
  

  
  const data = [];
  const points = [];
  for (let k=0;k<10; k++){
    data.push([]);
  }
  const walker_color = d3.interpolateLab("#0000ff", "#ff0000") 
  const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
  for (let j =0; j<walker_data.num_walkers; j++){
    let point = 0;
    let walker = [];
    for (let i =0; i<500; i++) {
      walker.push(pg.append("circle")
                  .attr("r", 3)
                  .attr("cx",x(0))
                  .attr("cy", y(0))  
                  .attr("fill", "black")
                  .attr("fill-opacity", 0.4));
    }
    points.push(walker);
  }
  const add_point = () => {
    for(let j=0; j <num_walkers;j++){
      let numPoints = data[j].slice(-500).length;
      data[j].slice(-500).forEach((m, i) => {
        points[j][i].attr("r", 1.5)
          .attr("cx",x(m[0]))
          .attr("cy", y(m[1]))  
          .attr("fill", walker_color((i+1)/numPoints))
          .attr("class","");
    })
    }
  };
  return {el:el, update: (d) => {
    d.forEach((m,i) => {data[i].push(m);})
     add_point();
  }}
  
}

const add_grad_desc_maps  = (parent_el, grad_desc_data) => {
  const plot = add_param_map(parent_el, grad_desc_data);
  const el = plot.el;
  const pd = plot.pd
  const x = plot.x;
  const y = plot.y;

  const lh_color = d3.interpolateHsl("red", "lime"); 

  const data = [];
  const currentPos = [0,0]
  const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
  const marker = pg.append("marker").attr("id","arrow").attr("markerWidth", 5).attr("markerHeight",5);
  marker.append('path').attr("d","M 0 0 L 10 5 L 0 10 z").attr("fill","context-fill").attr("stroke","context-stroke");
  const line = pg.append("line").attr("x1",0)
              .attr("x2",10)
              .attr("y1",0)
              .attr("y2",10)
              .attr("stroke", "red")
              .attr("stroke-width","3")
              .attr("marker-end","url(#arrow)");

  const update_line = (d,lh) => {
    line.attr("x1",x(currentPos[0])).attr("y1",y(currentPos[1])).attr("x2",x(d[0])).attr("y2",y(d[1])).attr("stroke",lh_color(lh/100));
    currentPos.length = 0;
    currentPos.push(d[0]);
    currentPos.push(d[1]);
    
  }

  return {el:el, update: (d,lh) => {
    update_line(d,lh);
    currentPos.length =0;
    currentPos.push(d[0]);
    currentPos.push(d[1]);
  }};
}

const add_osc_prob= (parent_el, prob_data) => {

  const pd = prob_data.plot_dims;

  const i = prob_data.prob_i;
  const lpos = prob_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = prob_data.y_start;
  const inter_between = prob_data.interpolate_between

  const el = parent_el.append("g")
                      .attr("transform", `translate(${lpos},${tpos})`)
                      .attr("class", prob_data.cls)
                      .attr("id", prob_data.cls + `-${i}`);

  // Declare the x (horizontal position) scale.
  const x = d3.scaleLinear()
      .domain(prob_data.xrange)
      .range([0, pd.w]);

  // Declare the y (vertical position) scale.
  const y = d3.scaleLinear()
      .domain(prob_data.yrange)
      .range([pd.h, 0]);

  const xax = el.append("g")
      .attr("class", prob_data.axiscls + "axis")
      .attr("transform", `translate(${pd.ml},${pd.h+pd.mt})`)
      .call(d3.axisBottom(x).ticks(pd.nxticks))

  xax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${pd.w*0.5}, ${pd.mb*0.75})`)
       .text(`Neutrino Energy [GeV]`);

  // Add the y-axis.
  const yax = el.append("g")
      .attr("class", prob_data.axiscls + "axis")
      .attr("transform", `translate(${pd.ml},${pd.mt})`)
      .call(d3.axisLeft(y).ticks(pd.nyticks))

  yax.append("text")
       .attr("text-anchor", "middle")
       .attr("transform", `translate(${-pd.ml*0.75}, ${pd.h*0.5}),rotate(270)`)
       .text(`${prob_data.ylabel}`);

  const nu_line = d3.line()
               .x((d) => { return x(d[0]); })
        .y((d) => { return y(d[1]); })


  let nu_line_true = null;
  if(prob_data.dotrue){
    nu_line_true = d3.line()
                 .x((d) => { return x(d[0]); })
      .y((d) => { return y(d[1]); });
  }

  let nu_line_ml = null
  if(prob_data.show_ml){
    nu_line_ml = d3.line()
                 .x((d) => { return x(d[0]); })
      .y((d) => { return y(d[1]); });
  }

  const data = [];
  const true_data = []
  const ml_data = []
  const build_path = (line, cls, d_source) => {
    const pg = el.append("g").attr("transform", `translate(${pd.ml},${pd.mt})`);
    const p = pg.append("path")
        .datum(d_source)
        .attr("class", cls)
        .attr("d", line);
    return [pg,p];
  };
    
  let nu_path = build_path(nu_line, prob_data.cls +"-series nu",data);
  let nu_path_true = null;
  let nu_path_ml;
  if(nu_line_true){
    nu_path_true = build_path(nu_line_true, prob_data.cls + "-series nutrue", true_data);
  }

  if(nu_line_ml){
    nu_path_ml = build_path(nu_line_ml, prob_data.cls + "-series numl", ml_data);
  }
  
  el.append("text")
    .attr("x", (pd.w/2))                    
    .attr("y", 20)
       .attr("text-anchor", "middle") 
    .text(prob_data.title);
  
  return {el:el, update: (d,d_t,d_ml,step) => {
    data.length =0
    if (step){
	let step_correction = (d[1][0] - d[0][0])/2;
	d.forEach((e)=>{data.push([e[0]-step_correction,e[1]])});
      }
      else{
	d.forEach((e)=>{data.push(e)});
      }
    if (inter_between){
      nu_path[1].transition()
    .duration(300).attr("d", nu_line)
    }
    else{
      nu_path[1].attr("d", nu_line)

    }
    if(nu_line_true){
      true_data.length = 0;
      if (step){
	let step_correction = (d_t[1][0] - d_t[0][0])/2;
	d_t.forEach((e)=>{true_data.push([e[0]-step_correction,e[1]])});
      }
      else{
	d_t.forEach((e)=>{true_data.push(e)});
      }
      nu_path_true[1].attr("d", nu_line_true);
     if (step){
       nu_line_true.curve(d3.curveStepAfter);
       nu_line.curve(d3.curveStepAfter);
      }
      else{
	nu_line_true.curve(d3.curveNatural);
	nu_line.curve(d3.curveNatural);
      }
    }
   if(nu_line_ml){
      ml_data.length = 0;
      if (step){
	let step_correction = (d_ml[1][0] - d_ml[0][0])/2;
	d_ml.forEach((e)=>{ml_data.push([e[0]-step_correction,e[1]])});
        nu_line_ml.curve(d3.curveStepAfter);
      }
      else{
	d_ml.forEach((e)=>{ml_data.push(e)});
        nu_line_ml.curve(d3.curveNatural);
      }
     nu_path_ml[1].attr("d", nu_line_ml);
  }}
         }};

const add_3flavor_triangle = (parent_el, flvtri_data) => {

  const pd = flvtri_data.plot_dims;
  pd.h = pd.w/2.0 * Math.tan(Math.PI/3.0);

  const i = flvtri_data.flvtri_i;
  const lpos = flvtri_data.x_start + i*(pd.w + pd.ml + pd.mb);
  const tpos = flvtri_data.y_start;

  //console.log(`translate(${lpos},${tpos})`);

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



//build UI starts here
const build_ui = (cfg) => {

  const scaff =  cfg.ui.scaffolding;

  const page_w = scaff.page.w;
  const page_h = scaff.page.h;

  const svg = d3.create("svg")
      .attr("width", page_w)
        .attr("height", page_h);

  const marker = svg.append("def").append("marker").attr("id","arrow").attr("markerWidth", 3).attr("markerHeight",3).attr("orient","auto-start-reverse").attr("refX",3).attr("refY",1.5);
  marker.append('path').attr("d","M 0 0 L 3 1.5 L 0 3 ").attr("fill","none").attr("stroke","context-stroke");

  const mode_choices = [];
  cfg.controls.modes.forEach((m, i)=>{
    mode_choices.push(add_mode_choice(svg, {i: i, label: m.label,
      w: scaff.mode_select.w, h: scaff.mode_select.h, lw: scaff.line.w,
      fs: scaff.mode_select.fs }));
  });


  const scaff_el = svg.append("g").attr("class", "scaffolding");

  
  //scaff.labels.forEach((m,i) =>{
    //draw_text(svg,{x: 450+ 200*i, y: 100, text:m.text}, "prob").attr("transform", `translate,rotate(270)`);
  //})

  let hline_height = scaff.mode_select.h + 2;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");
  hline_height += 2;

  const traces = [];
  cfg.ui.plots.traces.forEach((m, i) => {

    let param_i = null;
    //console.log(cfg.controls.parameters.length)
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
                                        plot_dims: scaff.plots.trace,
				        cls: ""}));
    }
  });

  let lh_trace = add_param_trace(svg, {trace_i: traces.length,
                                        param_i: 0,
                                        label: cfg.controls.likelihood[0].label,
                                        units: cfg.controls.likelihood[0].units,
                                        yrange: cfg.controls.likelihood[0].range,
                                        x_start : 0,
                                       y_start: hline_height,
                                       plot_dims: scaff.plots.trace,
				       cls: ""});


  hline_height += 2 + scaff.plots.trace.mt + scaff.plots.trace.h + scaff.plots.trace.mb;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");
  hline_height += 2;

  const mode_choice_re = mode_choices[mode_choices.length-1].re;
  const top_right_text = svg.append("g").attr("transform", `translate(${mode_choice_re}, 10)`);
  const bulbs = [];
  let colours = ["orange", "deeppink","lime", "darkviolet"]

  for (let i = 0; i<4; i++){
    bulbs.push(draw_updateable_circle(svg,{x:1100+i*35, y:15, color:colours[i], r:15}));
  }

  const text_elements = [];
  cfg.controls.status.forEach((m, i) => {
    text_elements.push(draw_updatable_text(top_right_text, {x: 10+ 200*i, y: 10}, (v) => { return (m.label + ` ${v}`); }, "ticker"));
  });

  const osc_events = [];
  cfg.ui.plots.osc_events.forEach((m, i) => {
    osc_events.push(add_osc_prob(svg, {prob_i: osc_events.length,
                                      ylabel: m.ylabel,
                                      xrange: m.xrange,
                                      yrange: m.yrange,
                                      x_start : 0,
                                      y_start: hline_height,
					    dobar: m.dobar,
					    dotrue:m.dotrue,
					    plot_dims: scaff.plots.osc_probability,
					    title:m.title,
					    cls:"prob",
					    axiscls:"",
				       interpolate_between:false,
                                       show_ml:true,}));

  });

  hline_height += 2 + scaff.plots.osc_probability.mt + scaff.plots.osc_probability.h + scaff.plots.osc_probability.mb;
  draw_line(scaff_el, { ends: [ [0, hline_height], [page_w, hline_height] ], lw:4 }, "scaffolding");

  hline_height += 26;

  draw_line(scaff_el, {ends:[[0, hline_height], [page_w,hline_height]], lw:4},"ml_scaffolding");

  
  let ml = cfg.ui.plots.machine_learning[0];
  const machine_learning = add_osc_prob(svg, {prob_i: 0,
                                      ylabel: ml.ylabel,
                                      xrange: ml.xrange,
                                      yrange: ml.yrange,
                                      x_start : 0,
                                      y_start: hline_height +40,
					    dobar: ml.dobar,
					    dotrue:ml.dotrue,
					    plot_dims: scaff.plots.osc_probability,
					    truth:ml.truth,
					    title:ml.title,
					      cls: "ml_prob",
					      axiscls:"ml_",
					      interpolate_between:true,
                                              show_ml:false,});
  
  let ml_lh_trace = add_param_trace(svg, {trace_i: 0,
                                        param_i: 0,
                                        label: cfg.controls.likelihood[1].label,
                                        units: cfg.controls.likelihood[1].units,
                                        yrange: cfg.controls.likelihood[1].range,
                                        x_start : scaff.plots.osc_probability.w + scaff.plots.osc_probability.ml + scaff.plots.ml_walker.ml,
                                        y_start: hline_height +60,
                                        plot_dims: scaff.plots.trace,
					cls: "ml_"});

  const ml_text_elements = [];
  cfg.ui.ml_status.forEach((m, i) => {
    ml_text_elements.push(draw_updatable_text(top_right_text, {x: 0 +200*i, y: hline_height + 40}, (v) => { return (m.label + ` ${v}`); }, "ml_prob"));
  });


  const ml_walkers = []

  cfg.ui.plots.ml_walker.forEach((m, i) => {
  ml_walkers.push(add_ml_walker(svg, {lh_i: ml_walkers.length,
                                    ylabel: m.ylabel,
                                    xlabel: m.xlabel,
                                      xrange: m.xrange,
                                      yrange: m.yrange,
                                      x_start : scaff.plots.osc_probability.w + scaff.plots.osc_probability.ml + scaff.plots.ml_walker.ml,
                                      y_start: hline_height +150,
                                      num_walkers:10,
					    plot_dims: scaff.plots.ml_walker,
					    title:m.title,
					    cls:"walker_param ml_prob",
					    axiscls:"ml_",
					    interpolate_between:false}));

  });

  const ml_grad_disp = []

  cfg.ui.plots.ml_walker.forEach((m, i) => {
  ml_grad_disp.push(add_grad_desc_maps(svg, {lh_i: ml_grad_disp.length,
                                    ylabel: m.ylabel,
                                    xlabel: m.xlabel,
                                      xrange: m.xrange,
                                      yrange: m.yrange,
                                      x_start : scaff.plots.osc_probability.w + scaff.plots.osc_probability.ml + scaff.plots.ml_walker.ml,
                                      y_start: hline_height +150,
                                      num_walkers:10,
					    plot_dims: scaff.plots.ml_walker,
					    title:m.title,
					    cls:"grad_desc_param ml_prob",
					    axiscls:"ml_",
					    interpolate_between:false}));

  });

  



  draw_line(scaff_el, {ends:[[0, hline_height  +scaff.plots.osc_probability.h+150], [page_w,hline_height +scaff.plots.osc_probability.h+150]], lw:4},"ml_scaffolding");

  hline_height += scaff.plots.flvtriangles.w +100;

  draw_line(scaff_el, {ends:[[0, hline_height], [page_w,hline_height]], lw:4},"scaffolding");

  const two_d_lhs = [];
  
  cfg.ui.plots.two_d_likelihood.forEach((m, i) => {
  two_d_lhs.push(add_two_d_lh(svg, {lh_i: two_d_lhs.length,
                                    ylabel: m.ylabel,
                                    xlabel: m.xlabel,
                                      xrange: m.xrange,
                                      yrange: m.yrange,
                                      x_start : 0,
                                      y_start: hline_height,
					    plot_dims: scaff.plots.two_d_likelihood,
					    title:m.title,
					    cls:"prob",
					    axiscls:"",
					    interpolate_between:false}));

  });

  // Append the SVG element.
  container.append(svg.node());

  return { traces: traces,
           text_elements: text_elements,
	   osc_events: osc_events,
	   machine_learning:machine_learning,
	   ml_text_elements:ml_text_elements,
	   ml_lh_trace:ml_lh_trace,
	   lh_trace:lh_trace,
	   bulbs:bulbs,
           two_d_lhs: two_d_lhs,
           ml_walkers: ml_walkers,
           ml_grad_disp:ml_grad_disp,
	 };
}
//Build UI ends here



const websocket = new WebSocket("ws://localhost:5678/");

let ui_els = null;
let trace_param = [];
let startTime = Date.now();
let once = true;
let likelihood = 0
let score_likelihood = 0
let noise = false
let hist = false
let slow_load = false
let ml = false
let ml_status = "in progress"
let dialog

let score = 0

function addScore(){
  let name = $('input[name=username]').val()
  if (name != ""){
    $.post("/add_score",{username:name,score:score, hist:hist, noise:noise, ml:ml, slow_load:slow_load});
  }
  dialog.dialog("close")
}
  
dialog = $( "#dialog" ).dialog({ autoOpen: false,
			modal: true,
			buttons: {
			  "Add Score": addScore,
			  Cancel: function() {
			    dialog.dialog( "close" );
			  }
			},
			close: function() {
			  form[ 0 ].reset();
			}
		      });
 
let form = dialog.find( "form" ).on( "submit", function( event ) {
   event.preventDefault();
      addScore();
 });

$(document).on("keypress", function( event ){
  
  let currentTime = Date.now();
  if (event.code == "Enter"){
    let name = $('input[name=username]').val()
  let currentTime = Date.now();
  if ((currentTime - startTime) > 300000){
    score = 1;
  }
  else{
    score = 300- ((currentTime - startTime)/1000);
    console.log(score)
    console.log("Time multiplier: " + 300- ((currentTime - startTime)/1000));
  }
  score *= score_likelihood;
  console.log("Likelihood  multiplier: " + score_likelihood);
  if (noise){
    score *=1.5;
  }
  
  if (hist){
    score *=1.5;
  }

    if (ml == "Complete"){
      score *=2
    }
  score = Math.round(score)
  $('#score-info').text("Your score is: " + score);
    dialog.dialog("open");
  }
});

websocket.onmessage = ({data}) => {
  const obj = JSON.parse(data);
 

  if (obj.cmd == "ui_start"){
    console.log("Building UI");
    //console.log(obj);
    ui_els = build_ui(obj.cfg.noec);
    $(".ml_prob").hide();
    $(".ml_trace").hide();
    $(".ml_scaffolding").hide()
   
    
     
  } else if(obj.cmd == "UPDATE"){
    //console.log(obj.osc_probs.numu)
    likelihood = obj.osc_probs.likelihood
    score_likelihood = obj.osc_probs.score_likelihood
    noise = obj.noise
    hist = obj.hist
    ml = obj.start_ml
    slow_load = obj.slow_load
    ui_els.traces.forEach( (m, i) => { if (obj.ADCStates[i] == true){ $("#trace-"+i).show();m.update(obj.vals[m.param_i]);} else{$("#trace-"+i).hide();} } );
    ui_els.lh_trace.update(obj.osc_probs.likelihood);
    ui_els.text_elements[0].update(obj.tick);
    ui_els.text_elements[1].update(obj.L_km);
    ui_els.text_elements[2].update(obj.osc_probs.likelihood)
    if (obj.start_ml){
      ui_els.osc_events[0].update(obj.osc_events.numu,obj.osc_events.numu_true,obj.osc_probs.mlnumu,true);
      ui_els.osc_events[1].update(obj.osc_events.nue,obj.osc_events.nue_true,obj.osc_probs.mlnue,true);
      ui_els.osc_events[2].update(obj.osc_events.bnue,obj.osc_events.bnue_true,obj.osc_probs.mlnueb,true);
    }
    else{
      ui_els.osc_events[0].update(obj.osc_events.nue,obj.osc_events.nue_true,[[0,0], [0,0]],true);
      ui_els.osc_events[1].update(obj.osc_events.nue,obj.osc_events.nue_true,[[0,0], [0,0]],true);
      ui_els.osc_events[2].update(obj.osc_events.bnue,obj.osc_events.bnue_true,[[0,0], [0,0]],true);
    }
    ui_els.bulbs[0].update(obj.hist);
    ui_els.bulbs[1].update(obj.noise)
    ui_els.bulbs[2].update(ml)
    ui_els.bulbs[3].update(slow_load)
    ui_els.two_d_lhs[0].update([obj.vals[1], obj.vals[0], likelihood]);
    ui_els.two_d_lhs[1].update([obj.vals[2], obj.vals[0], likelihood]);
    ui_els.two_d_lhs[2].update([obj.vals[2], obj.vals[1], likelihood]);
    if (obj.start_ml){
      $(".ml_prob").show();
      $(".ml_trace").show();
      $(".ml_scaffolding").show()
      ui_els.machine_learning.update(obj.osc_probs.mlnue,obj.osc_events.nue_true,false,true);
      ui_els.ml_text_elements[0].update(obj.ml_status);
      ui_els.ml_text_elements[1].update(obj.ml_likelihood);
      ui_els.ml_lh_trace.update(obj.ml_likelihood);
      if (obj.ml_mode == "MCMC"){
        $(".grad_desc_param").hide();
        $(".walker_param").show();
        ui_els.ml_walkers[0].update(obj.ml_walker_pos[0]);
        ui_els.ml_walkers[1].update(obj.ml_walker_pos[1]);
        ui_els.ml_walkers[2].update(obj.ml_walker_pos[2]);
      }
      else{
        $(".grad_desc_param").show();
        $(".walker_param").hide();
        ui_els.ml_grad_disp[0].update([obj.ml_grad_desc_vals[1], obj.ml_grad_desc_vals[0]], obj.ml_likelihood);
        ui_els.ml_grad_disp[1].update([obj.ml_grad_desc_vals[2], obj.ml_grad_desc_vals[0]], obj.ml_likelihood);
        ui_els.ml_grad_disp[2].update([obj.ml_grad_desc_vals[2], obj.ml_grad_desc_vals[1]], obj.ml_likelihood);
      }
      
    }
    else{
      $(".ml_prob").hide();
      $(".ml_trace").hide();
      $(".ml_scaffolding").hide()
    }
  }
};
