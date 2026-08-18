document.addEventListener("DOMContentLoaded", async () => {
  const chartCanvas = document.getElementById("feeding-chart");
  try {
    // Fetch historical data for the chart
    const response = await fetch("http://127.0.0.1:8000/history");
    const data = await response.json();
    const history = data.history;
    // Extract labels and datasets
    const labels = history.map(item => item.date);
    const feedCounts = history.map(item => item.count);
    const eatenGrams = history.map(item => Math.round(item.eaten));
    // Render Chart.js
    new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Food Eaten (g)",
            data: eatenGrams,
            type: "line", 
            borderColor: "#4a90e2",
            backgroundColor: "#4a90e2",
            tension: 0.3, 
            yAxisID: 'y1',
            order: 1
          },
          {
            label: "Feeding Count",
            data: feedCounts,
            backgroundColor: "#ff914d",
            yAxisID: 'y', 
            order: 2
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            type: 'linear',
            position: 'left',
            beginAtZero: true,
            title: { display: true, text: 'Count' }
          },
          y1: {
            type: 'linear',
            position: 'right',
            beginAtZero: true,
            grid: { drawOnChartArea: false }, // Prevent grid lines from overlapping
            title: { display: true, text: 'Weight (g)' }
          }
        }
      }
    });

    const predictionText = document.getElementById("feedings-prediction");
    const predictionContainer = predictionText.parentElement;
    
    predictionContainer.innerHTML = "<span><b>Calculating prediction...</b></span>";
    
    const predictResponse = await fetch("http://127.0.0.1:8000/predict-feeding");
    const predictData = await predictResponse.json();
    
    // Display the Data Science prediction
    predictionContainer.innerHTML = `<span><b>DS Prediction:</b> Your pet will need approximately <b>${predictData.predicted_meals} meals</b> (${predictData.predicted_grams}g total) tomorrow.</span>`;
  } catch (error) {
    console.error("Error fetching chart data:", error);
  }
});