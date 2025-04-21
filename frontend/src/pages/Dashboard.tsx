import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement, ArcElement } from 'chart.js';
import Layout from '../components/Layout';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement
);

interface Report {
  id: number;
  titulo: string;
  tipo: string;
  resultado: any;
  criado_em: string;
}

const Dashboard: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [filterTipo, setFilterTipo] = useState<string>('');
  const [filterDate, setFilterDate] = useState<string>('');

  useEffect(() => {
    fetchReports();
  }, [filterTipo, filterDate]);

  const fetchReports = async () => {
    try {
      let url = '/api/v1/relatorios/';
      const params: any = {};
      if (filterTipo) params.tipo = filterTipo;
      if (filterDate) params.criado_em = filterDate;
      const response = await axios.get(url, { params });
      setReports(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    }
  };

  const handleExport = (format: string) => {
    if (!selectedReport) return;
    const url = `/api/v1/relatorios/${selectedReport.id}/export/?format=${format}`;
    window.open(url, '_blank');
  };

  const chartData = selectedReport ? {
    labels: selectedReport.resultado.map((item: any) => item.label || item.name || ''),
    datasets: [
      {
        label: selectedReport.titulo,
        data: selectedReport.resultado.map((item: any) => item.value || item.count || 0),
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        borderColor: 'rgba(14, 165, 233, 1)',
        borderWidth: 1,
      },
    ],
  } : null;

  return (
    <Layout>
      <div className="mb-4 flex flex-col md:flex-row md:items-center md:space-x-4">
        <select
          className="border rounded p-2 mb-2 md:mb-0"
          value={filterTipo}
          onChange={(e) => setFilterTipo(e.target.value)}
        >
          <option value="">All Types</option>
          <option value="bar">Bar</option>
          <option value="line">Line</option>
          <option value="pie">Pie</option>
        </select>
        <input
          type="date"
          className="border rounded p-2"
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {reports.map((report) => (
          <div
            key={report.id}
            className={`p-4 border rounded cursor-pointer ${selectedReport?.id === report.id ? 'border-blue-500' : 'border-gray-300'}`}
            onClick={() => setSelectedReport(report)}
          >
            <h3 className="font-semibold">{report.titulo}</h3>
            <p className="text-sm text-gray-600">{new Date(report.criado_em).toLocaleDateString()}</p>
          </div>
        ))}
      </div>

      {selectedReport && chartData && (
        <div className="mt-6">
          <h2 className="text-xl font-bold mb-4">{selectedReport.titulo}</h2>
          {selectedReport.tipo === 'bar' && <Bar data={chartData} />}
          {selectedReport.tipo === 'line' && <Line data={chartData} />}
          {selectedReport.tipo === 'pie' && <Pie data={chartData} />}
          <div className="mt-4 space-x-2">
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              onClick={() => handleExport('json')}
            >
              Export JSON
            </button>
            <button
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              onClick={() => handleExport('csv')}
            >
              Export CSV
            </button>
            <button
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              onClick={() => handleExport('pdf')}
            >
              Export PDF
            </button>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default Dashboard;
