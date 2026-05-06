import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { format, subDays } from 'date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check if admin or customer
      const adminToken = localStorage.getItem('admin_token');
      const customerToken = localStorage.getItem('token');
      const isAdmin = !!adminToken;
      const token = adminToken || customerToken;
      
      if (!token) {
        throw new Error('Please login to view analytics');
      }

      // Use different endpoint for admin vs customer
      const endpoint = isAdmin 
        ? `http://localhost:8661/api/analytics/admin/overview?days=${days}`
        : `http://localhost:8661/api/analytics/dashboard?days=${days}`;

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized. Please login again.');
        }
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  // Check if admin or customer data format
  const isAdminData = analytics.feature_stats !== undefined;
  const isCustomerData = analytics.daily_usage !== undefined;

  // Prepare chart data based on format
  let dailyChartData = null;
  let featureChartData = null;
  let totalUsage = 0;
  let featureCount = 0;

  if (isCustomerData) {
    // Customer format: has daily_usage and feature_breakdown
    const dailyLabels = Object.keys(analytics.daily_usage).sort();
    const dailyData = dailyLabels.map(date => analytics.daily_usage[date]);

    dailyChartData = {
      labels: dailyLabels.map(date => format(new Date(date), 'MMM dd')),
      datasets: [
        {
          label: 'Daily Usage',
          data: dailyData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }
      ]
    };

    const featureLabels = Object.keys(analytics.feature_breakdown);
    const featureData = Object.values(analytics.feature_breakdown);

    featureChartData = {
      labels: featureLabels,
      datasets: [
        {
          label: 'Feature Usage',
          data: featureData,
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
          ],
          borderWidth: 1
        }
      ]
    };

    totalUsage = analytics.total_usage;
    featureCount = Object.keys(analytics.feature_breakdown).length;
  } else if (isAdminData) {
    // Admin format: has feature_stats and top_features
    const featureLabels = Object.keys(analytics.top_features || {});
    const featureData = featureLabels.map(f => analytics.top_features[f].usage_count);

    featureChartData = {
      labels: featureLabels,
      datasets: [
        {
          label: 'Feature Usage',
          data: featureData,
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)'
          ],
          borderWidth: 1
        }
      ]
    };

    totalUsage = analytics.total_usage;
    featureCount = Object.keys(analytics.feature_stats || {}).length;
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top'
      }
    }
  };

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h1>Usage Analytics</h1>
        <div className="date-filter">
          <label>Period: </label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>
      </div>

      <div className="stats-summary">
        <div className="stat-card">
          <h3>Total Usage</h3>
          <p className="stat-value">{totalUsage}</p>
          <p className="stat-label">actions tracked</p>
        </div>
        <div className="stat-card">
          <h3>Features Used</h3>
          <p className="stat-value">{featureCount}</p>
          <p className="stat-label">different features</p>
        </div>
        {isCustomerData && (
          <div className="stat-card">
            <h3>Average Daily</h3>
            <p className="stat-value">
              {Math.round(totalUsage / days)}
            </p>
            <p className="stat-label">actions per day</p>
          </div>
        )}
        {isAdminData && (
          <div className="stat-card">
            <h3>Unique Customers</h3>
            <p className="stat-value">{analytics.unique_customers}</p>
            <p className="stat-label">active users</p>
          </div>
        )}
      </div>

      <div className="charts-container">
        {dailyChartData && (
          <div className="chart-card">
            <h2>Daily Usage Trend</h2>
            <div className="chart-wrapper" style={{ height: '300px' }}>
              <Line data={dailyChartData} options={chartOptions} />
            </div>
          </div>
        )}

        {featureChartData && (
          <div className="chart-card">
            <h2>{isAdminData ? 'Top Features' : 'Feature Breakdown'}</h2>
            <div className="chart-wrapper" style={{ height: '300px' }}>
              <Bar data={featureChartData} options={chartOptions} />
            </div>
          </div>
        )}
      </div>

      <div className="feature-list">
        <h2>Feature Usage Details</h2>
        <table>
          <thead>
            <tr>
              <th>Feature</th>
              <th>Usage Count</th>
              {isAdminData && <th>Unique Customers</th>}
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {isCustomerData && Object.entries(analytics.feature_breakdown)
              .sort((a, b) => b[1] - a[1])
              .map(([feature, count]) => (
                <tr key={feature}>
                  <td>{feature}</td>
                  <td>{count}</td>
                  <td>
                    {((count / totalUsage) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            {isAdminData && Object.entries(analytics.feature_stats || {})
              .sort((a, b) => b[1].usage_count - a[1].usage_count)
              .map(([feature, stats]) => (
                <tr key={feature}>
                  <td>{feature}</td>
                  <td>{stats.usage_count}</td>
                  <td>{stats.unique_customers}</td>
                  <td>
                    {((stats.usage_count / totalUsage) * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <style>{`
        .analytics-dashboard {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .dashboard-header h1 {
          margin: 0;
          color: #333;
        }

        .date-filter {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .date-filter select {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .stats-summary {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
          margin: 0 0 10px 0;
          color: #666;
          font-size: 14px;
          font-weight: 500;
        }

        .stat-value {
          margin: 0;
          font-size: 32px;
          font-weight: bold;
          color: #333;
        }

        .stat-label {
          margin: 5px 0 0 0;
          color: #999;
          font-size: 12px;
        }

        .charts-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .chart-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .chart-card h2 {
          margin: 0 0 20px 0;
          font-size: 18px;
          color: #333;
        }

        .chart-wrapper {
          position: relative;
        }

        .feature-list {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .feature-list h2 {
          margin: 0 0 20px 0;
          font-size: 18px;
          color: #333;
        }

        .feature-list table {
          width: 100%;
          border-collapse: collapse;
        }

        .feature-list th,
        .feature-list td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #eee;
        }

        .feature-list th {
          background: #f5f5f5;
          font-weight: 600;
          color: #666;
        }

        .feature-list tr:hover {
          background: #f9f9f9;
        }

        .loading,
        .error {
          padding: 40px;
          text-align: center;
          font-size: 18px;
        }

        .error {
          color: #d32f2f;
        }

        @media (max-width: 768px) {
          .charts-container {
            grid-template-columns: 1fr;
          }

          .stats-summary {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default AnalyticsDashboard;
