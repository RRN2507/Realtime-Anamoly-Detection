import React from 'react';
import { Activity, Bell, CheckCircle2, TrendingUp, Info, UserCheck } from 'lucide-react';
import MetricsCard from './MetricsCard';
import AlertsList from './AlertsList';
import VolumeChart from './VolumeChart';
import { useMetrics } from '../hooks/useMetrics';
import { useAlerts } from '../hooks/useAlerts';

const Dashboard = () => {
  const { metrics, history } = useMetrics();
  const alerts = useAlerts();

  return (
    <div className="relative min-h-screen bg-[#f8fafc]">
      <div className="ambient-soft" />
      
      {/* Friendly Header */}
      <header className="max-w-7xl mx-auto px-6 pt-12 pb-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-indigo-100 text-indigo-600 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                Live Status
              </span>
              <div className="flex items-center gap-1.5 text-emerald-600 text-xs font-semibold">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                System is healthy
              </div>
            </div>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">
              Transaction Overview
            </h1>
            <p className="text-slate-500 mt-2 text-lg font-medium">
              Monitoring your financial stream for unusual activity.
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="bg-white px-4 py-2 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
              <UserCheck size={20} className="text-slate-400" />
              <div className="text-right">
                <p className="text-[10px] font-bold text-slate-400 uppercase leading-none">Operator</p>
                <p className="text-sm font-semibold text-slate-700 leading-none mt-1">Administrator</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pb-20">
        {/* Simplified Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <MetricsCard 
            label="Activity Level" 
            value={metrics.throughput} 
            unit="items/sec"
            subtitle="Current processing volume"
            icon={<TrendingUp size={24} className="text-indigo-500" />}
          />
          <MetricsCard 
            label="Processing Speed" 
            value={metrics.latency_ms} 
            unit="ms"
            subtitle="Average response time"
            icon={<Activity size={24} className="text-blue-500" />}
          />
          <MetricsCard 
            label="AI Guardian" 
            value="Active" 
            unit="v1.0"
            subtitle="Anomaly detection engine"
            icon={<CheckCircle2 size={24} className="text-emerald-500" />}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* Main Visual Area */}
          <div className="lg:col-span-2">
            <div className="human-card p-10 h-[500px] flex flex-col">
              <div className="flex items-start justify-between mb-10">
                <div>
                  <h3 className="text-xl font-bold text-slate-900">Activity Trends</h3>
                  <p className="text-sm text-slate-500 mt-1 italic">Visualizing the flow of transactions over time</p>
                </div>
                <button className="text-slate-400 hover:text-slate-600 transition-colors">
                  <Info size={20} />
                </button>
              </div>
              <div className="flex-1 min-h-0">
                <VolumeChart history={history} />
              </div>
            </div>
          </div>

          {/* Actionable Alerts Area */}
          <div className="lg:col-span-1">
            <div className="human-card overflow-hidden h-[500px] flex flex-col border-none shadow-[0_20px_50px_rgba(0,0,0,0.05)]">
              <div className="px-8 py-6 bg-slate-900 text-white flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell size={20} className="text-amber-400" />
                  <h3 className="text-lg font-bold">Unusual Activity</h3>
                </div>
                {alerts.length > 0 && (
                  <span className="bg-white/20 px-2 py-0.5 rounded-lg text-xs font-bold">
                    {alerts.length}
                  </span>
                )}
              </div>
              <div className="flex-1 overflow-hidden">
                <AlertsList alerts={alerts} />
              </div>
              <div className="p-4 bg-slate-50 border-t border-slate-100 text-center">
                <button className="text-indigo-600 text-xs font-bold uppercase tracking-widest hover:text-indigo-700 transition-colors">
                  View Full History
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
