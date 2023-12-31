(function() {

  const { Plugin }  = g3wsdk.core.plugin;
  const { GUI }     = g3wsdk.gui;
  const { G3W_FID } = g3wsdk.constant;
  const pid         = 'qps-timeseries';

  if (!globalThis.Plotly) {
    $script('https://cdn.plot.ly/plotly-1.52.2.min.js');
  }

  document.head.insertAdjacentHTML(
    'beforeend',
    `<style>
      .${pid} .js-plotly-plot                     { margin-bottom: 30px; }
      .${pid} .bootbox-close-button               { width: 40px; font-size: 40px; z-index: 1; position: absolute; right: 15px; }
      .${pid} .modebar-container                  { top: unset !important; bottom: 0; left: 0; text-align: center; }
      .${pid} .modebar-btn                        { font-size: 30px !important; }
      .${pid} .modebar                            { left: 0; }
      .${pid} .modebar-container > div            { display: flex; flex-wrap: wrap; justify-content: space-between; }
      .${pid} .modebar-group:nth-last-child(-n+3) { order: -1; }
      .${pid} .modebar-group:nth-child(2)         { margin-left: auto }
      .${pid} .modebar-group:first-of-type        { order: 2; }
      .${pid} .modebar-group:nth-last-child(-n+2) { order: 1; margin-left: auto; }
      .${pid} .modebar-group:last-of-type         { position: fixed; left: 0; top: 8px; }
      .${pid} .rangeslider-rangeplot.xy           { opacity: .15; }
      .${pid} :is(.rangeslider-handle-min, .rangeslider-handle-max) { height: 21px; width: 8px; translate: -2px -5px; fill: yellow; shape-rendering: optimizespeed; }
      @media (max-width: 992px) {
        .${pid} .modal-dialog  { width: 100%; height: 100%; margin: 0; padding: 0; }
        .${pid} .modal-content { height: auto; min-height: 100%; border-radius: 0; }
      }
      body:not(.skin-yellow) .${pid} .modebar-group:nth-last-child(-n+3):not(:nth-last-child(-n+2)) { display: none; }
    </style>`,
  );

  /**
   * Custom modebar button
   * 
   * @see https://plotly.com/javascript/configuration-options/#add-buttons-to-modebar
   */
  const btn = (name, color, data, ids) => ({
    name,
    icon: {
      svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -4 39 9" style="fill:${ color }; stroke:${ color }; stroke-width: 2; opacity:${ 'markers' == data[ids[0]].mode ? 0.5 : 1 }"><path d="M5,0h30M24,4h-8v-8h8v8Z"/></svg>`
    },
    click(p, e) {
      const btn = e.target.closest('.modebar-btn svg');
      const off = btn.style.opacity < 1;
      Plotly.restyle(p, { mode: off ? 'scatter' : 'markers' }, ids);
      btn.style.opacity = off ? 1 : .5;
    }
  });

  new (class extends Plugin {
    constructor() {
      super({
        name: 'qps_timeseries',
        i18n: {},
      });
      if (this.registerPlugin(this.config.gid)) {
        GUI
          .getService('queryresults')
          .onafter('addActionsForLayers', (actions, layers) => {
            layers.forEach(layer => {
              if (!this.config.layers.includes(layer.id)) {
                return;
              }
              actions[layer.id].push({
                id: pid,
                class: GUI.getFontClass('chart-line'),
                hint: 'PS Time Series',
                cbk: (layer, feature) => {
                  const chart = new (Vue.extend({
                    template: `<section><bar-loader :loading="loading"/><div ref="chart"></div></section>`,
                    data:     () => ({ loading: true }), // show loading bar while getting data from server
                  }))();
                  GUI
                    .showModalDialog({
                      message: chart.$mount().$el,
                      size: 'large',
                      className: pid,
                    })
                    .on("shown.bs.modal", async function() {
                      try {
                        const { data, layout, config } = await (await fetch(initConfig.baseurl + 'qps_timeseries/api/plot/'+ initConfig.group.initproject.split(':')[1] +  '/' + layer.id + '/' + feature.attributes[G3W_FID])).json();  
                        data[1].x = data[2].x = data[0].x; // trace replicas
                        Plotly.newPlot(chart.$refs.chart, data, layout, {...config, modeBarButtonsToAdd: [
                            [
                              {
                                name: 'Add replica lines',
                                icon: {
                                  width: 448,
                                  height: 512,
                                  path: 'm428 381-197 97a19 19 0 0 1-14 1L20 381c-4-2-4-6 0-8l47-23a19 19 0 0 1 15 0l135 67a19 19 0 0 0 14 0l135-67a19 19 0 0 1 15 0l47 23c4 2 4 6 0 8zm0-137-47-23a19 19 0 0 0-15 0l-135 67a19 19 0 0 1-15 0L83 221a19 19 0 0 0-15 0l-47 23c-4 2-4 5 0 7l197 98a19 19 0 0 0 14 0l197-98c4-2 4-5 0-7zM20 130l197 91a20 20 0 0 0 14 0l197-91c4-2 4-5 0-6L231 33a20 20 0 0 0-14 0L20 124c-4 2-4 5 0 6z'
                                },
                                click(p, e) {
                                  const delta = Math.abs(+prompt('Replica delta [mm]'));
                                  if (!delta || !isFinite(delta)) {
                                    return Plotly.update(chart.$refs.chart, { visible: false }, {}, [1, 2]);
                                  }
                                  Plotly.update(chart.$refs.chart, { name: `Replica +${delta}`, y: [data[0].y.map(y => y+delta)], visible: true }, {}, [1]);
                                  Plotly.update(chart.$refs.chart, { name: `Replica -${delta}`, y: [data[0].y.map(y => y-delta)], visible: true }, {}, [2]);
                                },
                              },
                              {
                                name: 'Toggle grid lines',
                                icon: {
                                  svg: `<svg id="${pid}-grid" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><style>#${pid}-grid{fill:#c6c6c6}#${pid}-grid:hover{fill:#7b7b7b}#${pid}-grid.x>path:nth-of-type(1),#${pid}-grid.y>path:nth-of-type(2),#${pid}-grid:not(.y.x)>path:nth-of-type(3){display: none}</style><path d="M74 246c-3 0-5-2-5-5V15a5 5 0 0 1 10 0v226c0 3-2 5-5 5zm54 0c-3 0-5-2-5-5V15a5 5 0 0 1 10 0v226c0 3-2 5-5 5zm54 0c-3 0-5-2-5-5V15a5 5 0 0 1 10 0v226c0 3-2 5-5 5z"/><path d="M241 79H15a5 5 0 0 1 0-10h226a5 5 0 0 1 0 10zm0 54H15a5 5 0 0 1 0-10h226a5 5 0 0 1 0 10zm0 54H15a5 5 0 0 1 0-10h226a5 5 0 0 1 0 10z"/><path d="M241 20H15a5 5 0 0 1 0-10h226a5 5 0 0 1 0 10zm0 226H15a5 5 0 0 1 0-10h226a5 5 0 0 1 0 10zm-226 0c-3 0-5-2-5-5V15a5 5 0 0 1 10 0v226c0 3-2 5-5 5zm226 0c-3 0-5-2-5-5V15a5 5 0 0 1 10 0v226c0 3-2 5-5 5z"/></svg>`,
                                },
                                click(p, e) {
                                  let x = layout.xaxis.showgrid; 
                                  let y = layout.yaxis.showgrid;
                                  Plotly.relayout(chart.$refs.chart, { 'xaxis.showgrid': !x || (!y && y), 'yaxis.showgrid': (x && y) || (!x && !y) });
                                },
                              },
                              btn('Toggle scatter lines', 'black', data, [0]),
                              btn('Toggle replica lines', 'blue', data, [1, 2]),
                            ], [
                              initConfig?.user?.admin_url && {
                                name: 'Edit in admin',
                                icon: Plotly.Icons.pencil,
                                direction: 'up',
                                click(gd) {
                                  window.open(initConfig.user.admin_url + 'qps_timeseries/projects/', '_blank');
                                },
                              },
                            ].filter(Boolean), [{
                              name: 'Download plot as svg',
                              icon: {
                                width: 70,
                                height: 70,
                                path: 'M60.64,62.3a11.29,11.29,0,0,0,6.09-6.72l6.35-17.72L60.54,25.31l-17.82,6.4c-2.36.86-5.57,3.41-6.6,6L24.48,65.5l8.42,8.42ZM40.79,39.63a7.89,7.89,0,0,1,3.65-3.17l14.79-5.31,8,8L61.94,54l-.06.19a6.44,6.44,0,0,1-3,3.43L34.07,68l-3.62-3.63Zm16.57,7.81a6.9,6.9,0,1,0-6.89,6.9A6.9,6.9,0,0,0,57.36,47.44Zm-4,0a2.86,2.86,0,1,1-2.85-2.85A2.86,2.86,0,0,1,53.32,47.44Zm-4.13,5.22L46.33,49.8,30.08,66.05l2.86,2.86ZM83.65,29,70,15.34,61.4,23.9,75.09,37.59ZM70,21.06l8,8-2.84,2.85-8-8ZM87,80.49H10.67V87H87Z',
                                transform: 'matrix(1 0 0 1 -15 -15)'
                              },
                              click(gd) {
                                Plotly.downloadImage(gd, { ...config.toImageButtonOptions, format: 'svg' })
                              }
                            }],
                          ],
                        });
                        chart.$refs.chart.on('plotly_afterplot', function() {
                          // show replica lines toggler
                          document.querySelector(`.${pid} .modebar-group:nth-last-child(-n+4) .modebar-btn:last-of-type`).hidden = !data[1].visible && !data[2].visible;
                          // cycle grid lines toggler
                          const svg = document.querySelector(`.${pid} .modebar-group:nth-last-child(-n+4) .modebar-btn:nth-of-type(2) svg`)
                          svg.classList.toggle('x',!layout.xaxis.showgrid);
                          svg.classList.toggle('y',!layout.yaxis.showgrid);
                        })
                      } catch(e) {
                        chart.$refs.chart.innerHTML = `<h1>Uh oh, something went wrong:</h1><p>${e.toString()}</p><a target="_blank" href="https://github.com/g3w-suite/g3w-admin-ps-timeseries/issues/new?title=${e.toString()}&labels=bug" style="position: fixed;inset: auto 0 1em 0;text-align: center;display: block;"><svg xmlns="http://www.w3.org/2000/svg" fill="#222" viewBox="0 0 32 32" style="width: 16px;vertical-align: sub;"><path d="M 5.6875 5 C 5.6875 5 5 6.207031 5 8.25 C 5 9.605469 5.308594 10.320313 5.53125 10.6875 C 3.96875 12.3125 3 14.515625 3 17.34375 C 3 24.585938 7.589844 27 16 27 C 24.410156 27 29 24.585938 29 17.34375 C 29 14.417969 28.085938 12.21875 26.59375 10.625 C 26.964844 9.515625 27.382813 7.421875 26.34375 5 C 23.242188 5 20.65625 7.382813 20.5625 7.46875 C 19.113281 7.152344 17.574219 7 16 7 C 14.394531 7 12.820313 7.195313 11.34375 7.5625 C 9.265625 5.503906 6.757813 5 5.6875 5 Z M 20.6875 15.4375 C 21.53125 15.429688 22.3125 15.5 23 15.71875 C 24.832031 16.300781 26 17.984375 26 19.875 C 26 25.109375 23.191406 26 16 26 C 10.65625 26 6.3125 25.058594 6.3125 20.0625 C 6.3125 18.15625 7.347656 17.078125 8.09375 16.40625 C 9.734375 14.929688 12.324219 15.65625 16 15.65625 C 17.671875 15.65625 19.277344 15.453125 20.6875 15.4375 Z M 10.5 18 C 9.671875 18 9 18.894531 9 20 C 9 21.105469 9.671875 22 10.5 22 C 11.328125 22 12 21.105469 12 20 C 12 18.894531 11.328125 18 10.5 18 Z M 21.5 18 C 20.671875 18 20 18.894531 20 20 C 20 21.105469 20.671875 22 21.5 22 C 22.328125 22 23 21.105469 23 20 C 23 18.894531 22.328125 18 21.5 18 Z M 10.34375 18.84375 C 10.578125 18.84375 10.75 19.042969 10.75 19.28125 C 10.75 19.519531 10.578125 19.71875 10.34375 19.71875 C 10.109375 19.71875 9.90625 19.519531 9.90625 19.28125 C 9.90625 19.042969 10.109375 18.84375 10.34375 18.84375 Z M 21.34375 18.84375 C 21.578125 18.84375 21.75 19.042969 21.75 19.28125 C 21.75 19.519531 21.578125 19.71875 21.34375 19.71875 C 21.109375 19.71875 20.90625 19.519531 20.90625 19.28125 C 20.90625 19.042969 21.109375 18.84375 21.34375 18.84375 Z"></path></svg> Report this issue </a>`;
                      } finally{ 
                        chart.loading = false;
                      }
                    });
                }
              });
            });
          });
      }
      // hide loading icon on map
      this.setReady(true);
    }
  })();

})();