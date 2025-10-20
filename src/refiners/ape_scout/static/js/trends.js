(function () {
  const canvases = document.querySelectorAll('canvas.trend-chart');
  canvases.forEach((canvas) => {
    const data = JSON.parse(canvas.dataset.trend || '[]');
    if (!data.length) {
      canvas.replaceWith(document.createTextNode('暂无数据'));
      return;
    }
    const labels = data.map((entry) => entry.date.slice(5));
    const mentions = data.map((entry) => entry.mentions);
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            data: mentions,
            fill: false,
            borderColor: '#6366f1',
            tension: 0.3,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: false,
        animation: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true },
        },
        scales: {
          x: {
            ticks: { display: false },
            grid: { display: false },
          },
          y: {
            ticks: { display: false },
            grid: { display: false },
          },
        },
      },
    });
  });
})();
