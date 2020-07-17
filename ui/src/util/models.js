var blankChart = {
  series: [],
  options: {
    chart: {
      type: 'bar',
      stacked: true,
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    responsive: [{
      breakpoint: 480,
      options: {
        legend: {
          position: 'bottom',
          offsetX: -10,
          offsetY: 0
        }
      }
    }],
    plotOptions: {
      bar: {
        horizontal: false,
      },
    },
    xaxis: {
      type: 'category',
      categories: [],
      tickPlacement: 'on'
    },
    legend: {
      position: 'bottom'
    },
    fill: {
      opacity: 1
    }
  }
}

export { blankChart };