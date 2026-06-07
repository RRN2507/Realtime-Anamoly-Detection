import React from 'react';

const MetricsCard = ({ label, value, unit, subtitle, icon }) => (
  <div className="human-card p-8 group">
    <div className="flex items-start justify-between mb-4">
      <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100 group-hover:bg-indigo-50 group-hover:border-indigo-100 transition-colors duration-300">
        {icon}
      </div>
    </div>
    
    <div>
      <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">{label}</p>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
          {typeof value === 'number' ? Math.round(value).toLocaleString() : value}
        </span>
        <span className="text-sm font-bold text-slate-400 lowercase">{unit}</span>
      </div>
      <p className="text-sm text-slate-500 font-medium">{subtitle}</p>
    </div>
  </div>
);

export default MetricsCard;
