var blankChart = {
  series: [],
  options: {
    colors: ['#ec7063', '#5499c7', '#45b39d', '#f4d03f', '#3440eb', '#af7ac5', '#ebc634', '#34ebcd', '#eb3434', '#eb7a34', '#eb34d3', '#c9eb34', '#34a2eb', '#7aeb34', '#34eb6e', '#a834eb', '#eb3465'],
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