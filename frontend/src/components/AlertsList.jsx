import React from 'react';
import { User, DollarSign, Clock, ShieldAlert } from 'lucide-react';

const AlertsList = ({ alerts }) => {
  if (alerts.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center space-y-4 p-12 text-center opacity-60">
        <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center">
          <Clock size={32} className="text-slate-300" />
        </div>
        <p className="text-sm font-medium text-slate-500">Everything looks normal right now.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar">
      {alerts.map((alert, idx) => (
        <div key={alert.id || idx} className="alert-item group">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.4)]" />
              <span className="text-[10px] font-black text-rose-500 uppercase tracking-widest">
                Anomaly Detected
              </span>
            </div>
            <span className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-1 rounded-full border border-slate-100">
              {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          </div>

          <div className="flex items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-500">
                <User size={18} />
              </div>
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mb-0.5">User Account</p>
                <p className="text-sm font-bold text-slate-700">{alert.user_id}</p>
              </div>
            </div>
            
            <div className="text-right">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mb-0.5">Flagged Amount</p>
              <p className="text-xl font-black text-slate-900 leading-none">
                ${alert.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
            </div>
          </div>
          
          <div className="mt-5 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="flex items-center gap-1.5 text-rose-600 font-bold text-[10px] uppercase">
              <ShieldAlert size={12} />
              High Risk Pattern
            </div>
            <button className="bg-slate-900 text-white px-3 py-1 rounded-lg text-[10px] font-bold hover:bg-indigo-600 transition-colors">
              Review Transaction
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertsList;
