import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
});

export const getMetrics = async () => {
  const response = await client.get('/metrics');
  return response.data;
};

export const getDashboard = async () => {
  const response = await client.get('/dashboard');
  return response.data;
};
