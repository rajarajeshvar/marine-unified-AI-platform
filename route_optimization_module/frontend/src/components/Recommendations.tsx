"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Info, CheckCircle } from "lucide-react";

export default function Recommendations({ recommendations }: { recommendations: any[] }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
      <h3 className="text-xl font-semibold mb-4 text-slate-100">AI Recommendations</h3>
      <div className="space-y-4">
        {recommendations.map((rec, idx) => {
          let Icon = Info;
          let color = "text-blue-400";
          let bg = "bg-blue-900/20";
          let border = "border-blue-800";

          if (rec.type === "warning") {
            Icon = AlertTriangle;
            color = "text-amber-400";
            bg = "bg-amber-900/20";
            border = "border-amber-800";
          } else if (rec.type === "success") {
            Icon = CheckCircle;
            color = "text-emerald-400";
            bg = "bg-emerald-900/20";
            border = "border-emerald-800";
          }

          return (
            <motion.div
              key={rec.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-start gap-3 p-4 rounded-md border ${border} ${bg}`}
            >
              <Icon className={`w-6 h-6 ${color} shrink-0 mt-0.5`} />
              <p className="text-slate-200">{rec.message}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
