import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

const VolumeChart = ({ history }) => {
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        grid: { 
          color: 'rgba(0, 0, 0, 0.03)',
          drawBorder: false
        },
        ticks: { 
          color: '#94a3b8', 
          font: { size: 11, family: 'Inter' },
          padding: 10
        }
      },
      x: {
        grid: { display: false },
        ticks: { 
          color: '#94a3b8', 
          font: { size: 11, family: 'Inter' },
          maxTicksLimit: 10
        }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1e293b',
        titleFont: { size: 13, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 16,
        borderRadius: 12,
        displayColors: false,
        callbacks: {
          label: (context) => `Processing ${context.parsed.y} items/sec`
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index',
    },
  };

  const data = {
    labels: history.map(h => h.time),
    datasets: [
      {
        fill: true,
        label: 'Flow',
        data: history.map(h => h.value),
        borderColor: '#6366f1',
        borderWidth: 4,
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, 'rgba(99, 102, 241, 0.08)');
          gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
          return gradient;
        },
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#6366f1',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 4,
      },
    ],
  };

  return (
    <div className="w-full h-full">
      <Line options={options} data={data} />
    </div>
  );
};

export default VolumeChart;
