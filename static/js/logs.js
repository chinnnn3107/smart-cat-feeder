import { authFetch } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {
  const chartCanvas = document.getElementById("feeding-chart");
  
  try {
    // Get history data from backend (token injected automatically by authFetch)
    const response = await authFetch("http://127.0.0.1:8000/history");
    const data = await response.json();
    const history = data.history;
    
    // Prepare data for the chart
    const labels = history.map(item => item.date);
    const feedCounts = history.map(item => item.count);
    const eatenGrams = history.map(item => Math.round(item.eaten));
    
    // Draw the chart using Chart.js
    new Chart(chartCanvas, {
      type: "bar", // Default to bar chart
      data: {
        labels: labels, // X-axis labels
        datasets: [
          {
            label: "Food Eaten (g)",
            data: eatenGrams,
            type: "line", // Draw as a line
            borderColor: "#4a90e2",
            backgroundColor: "#4a90e2",
            tension: 0.3, // Curve the line slightly
            yAxisID: 'y1', // Use the right Y-axis
            order: 1 // Draw on top
          },
          {
            label: "Feeding Count",
            data: feedCounts,
            backgroundColor: "#ff914d",
            yAxisID: 'y', // Use the left Y-axis
            order: 2 // Draw below the line
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: { // Left axis settings
            type: 'linear',
            position: 'left',
            beginAtZero: true,
            title: { display: true, text: 'Count' }
          },
          y1: { // Right axis settings
            type: 'linear',
            position: 'right',
            beginAtZero: true,
            grid: { drawOnChartArea: false }, // Prevent grid overlap
            title: { display: true, text: 'Weight (g)' }
          }
        }
      }
    });

    // Show loading state for prediction
    const predictionText = document.getElementById("feedings-prediction");
    const predictionContainer = predictionText.parentElement;
    predictionContainer.innerHTML = "<span><b>Calculating prediction...</b></span>";
    
    // Get and show prediction data
    const predictResponse = await authFetch("http://127.0.0.1:8000/predict-feeding");
    const predictData = await predictResponse.json();
    predictionContainer.innerHTML = `<span><b>DS Prediction:</b> Your pet will need approximately <b>${predictData.predicted_meals} meals</b> (${predictData.predicted_grams}g total) tomorrow.</span>`;
    
  } catch (error) {
    console.error("Error fetching chart data:", error);
  }
});