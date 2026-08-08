'use client';

import { useState, useRef, useCallback } from 'react';
import { ScanLine, Upload, Trash2, Zap, AlertTriangle, CheckCircle, Clock, Image as ImageIcon, ChevronLeft, Activity, Shield, Eye } from 'lucide-react';
import Link from 'next/link';

const API_BASE = 'http://localhost:8004';

interface Detection {
  class_name: string;
  confidence: number;
  bbox_xyxy: number[];
}

interface PredictionResult {
  num_detections: number;
  inference_time_ms: number;
  model_variant: string;
  image_size: { width: number; height: number };
  detections: Detection[];
  annotated_image_base64: string | null;
}

export default function HullCrackFinderPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handlePredict = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data: PredictionResult = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const severityColor = (n: number) => {
    if (n === 0) return 'text-emerald-400';
    if (n <= 2) return 'text-amber-400';
    return 'text-red-400';
  };

  const severityLabel = (n: number) => {
    if (n === 0) return 'CLEAR';
    if (n <= 2) return 'MODERATE';
    return 'CRITICAL';
  };

  return (
    <div className="min-h-[calc(100vh-140px)] bg-slate-950 text-slate-100 p-6 font-mono">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <ScanLine className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 tracking-wide uppercase">
              Hull Crack Detection
            </h1>
            <p className="text-[10px] text-slate-500 tracking-widest uppercase">
              YOLOv8 · Structural Analysis · Port 8004
            </p>
          </div>
          {/* Live indicator */}
          <div className="flex items-center gap-1.5 ml-4 px-2 py-0.5 rounded border border-cyan-900/60 bg-cyan-950/20">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-[9px] text-cyan-400 tracking-widest uppercase">API Live</span>
          </div>
        </div>
        <Link
          href="/"
          className="flex items-center gap-1.5 text-[10px] text-slate-500 hover:text-slate-300 transition-colors uppercase tracking-wider"
        >
          <ChevronLeft className="w-3 h-3" />
          Back to Console
        </Link>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        {/* LEFT PANEL — Upload + Controls */}
        <div className="xl:col-span-2 flex flex-col gap-4">

          {/* Drop Zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 select-none
              ${dragOver
                ? 'border-cyan-400 bg-cyan-950/20 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
                : 'border-slate-700 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/60'
              }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.bmp,.tiff,.webp"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
            <Upload className={`w-8 h-8 mx-auto mb-3 ${dragOver ? 'text-cyan-400' : 'text-slate-600'}`} />
            <p className="text-xs text-slate-400">
              {dragOver ? 'Release to upload' : 'Drop hull image here or click to browse'}
            </p>
            <p className="text-[10px] text-slate-600 mt-1 uppercase tracking-wider">
              JPG · PNG · BMP · TIFF · WebP
            </p>
          </div>

          {/* File info + controls */}
          {selectedFile && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2 text-[10px] text-slate-400 uppercase tracking-wider">
                <ImageIcon className="w-3 h-3" />
                <span className="flex-1 truncate text-slate-300">{selectedFile.name}</span>
                <span className="text-slate-600">{(selectedFile.size / 1024).toFixed(0)} KB</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handlePredict}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded border border-cyan-800 bg-cyan-950/40 text-cyan-400 text-[11px] font-bold uppercase tracking-widest hover:bg-cyan-900/40 hover:border-cyan-600 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-[inset_0_0_8px_rgba(34,211,238,0.05)]"
                >
                  {loading ? (
                    <>
                      <Activity className="w-3.5 h-3.5 animate-pulse" />
                      Analysing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-3.5 h-3.5" />
                      Run Detection
                    </>
                  )}
                </button>
                <button
                  onClick={handleClear}
                  className="px-3 py-2.5 rounded border border-slate-700 bg-slate-900 text-slate-500 hover:text-slate-300 hover:border-slate-600 transition-all text-[11px] uppercase tracking-wider"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2.5 p-3.5 rounded-lg border border-red-900/60 bg-red-950/30">
              <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-[10px] uppercase tracking-wider text-red-400 font-bold mb-0.5">Detection Error</p>
                <p className="text-xs text-red-300/80">{error}</p>
                {error.includes('503') || error.includes('model') && (
                  <p className="text-[10px] text-red-500/70 mt-1">
                    Model weights not found. Train the model first via <code className="font-mono">python scripts/train.py</code>
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Stats Cards (after result) */}
          {result && (
            <div className="space-y-3">
              {/* Severity Banner */}
              <div className={`rounded-lg border p-4 flex items-center gap-3
                ${result.num_detections === 0
                  ? 'border-emerald-900/60 bg-emerald-950/20'
                  : result.num_detections <= 2
                    ? 'border-amber-900/60 bg-amber-950/20'
                    : 'border-red-900/60 bg-red-950/20'
                }`}>
                {result.num_detections === 0
                  ? <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                  : <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                }
                <div>
                  <p className={`text-sm font-bold tracking-wider uppercase ${severityColor(result.num_detections)}`}>
                    {severityLabel(result.num_detections)}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {result.num_detections === 0
                      ? 'No structural damage detected'
                      : `${result.num_detections} crack region${result.num_detections > 1 ? 's' : ''} detected`}
                  </p>
                </div>
              </div>

              {/* Metric Grid */}
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Detections', value: result.num_detections, icon: Eye },
                  { label: 'Inference', value: `${result.inference_time_ms.toFixed(0)} ms`, icon: Clock },
                  { label: 'Model', value: result.model_variant, icon: Shield },
                  { label: 'Resolution', value: `${result.image_size.width}×${result.image_size.height}`, icon: ImageIcon },
                ].map(({ label, value, icon: Icon }) => (
                  <div key={label} className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Icon className="w-3 h-3 text-slate-600" />
                      <span className="text-[9px] uppercase tracking-widest text-slate-600">{label}</span>
                    </div>
                    <p className="text-sm font-bold text-slate-200">{value}</p>
                  </div>
                ))}
              </div>

              {/* Detections Table */}
              {result.detections.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-lg overflow-hidden">
                  <div className="px-3 py-2 border-b border-slate-800 text-[9px] uppercase tracking-widest text-slate-600 grid grid-cols-4 gap-2">
                    <span>#</span>
                    <span>Class</span>
                    <span>Confidence</span>
                    <span>Bbox (xyxy)</span>
                  </div>
                  {result.detections.map((det, i) => (
                    <div key={i} className="px-3 py-2 grid grid-cols-4 gap-2 text-xs border-b border-slate-800/50 last:border-0 hover:bg-slate-800/20">
                      <span className="text-slate-600">{i + 1}</span>
                      <span className="text-cyan-400 font-bold capitalize">{det.class_name}</span>
                      <span className="text-slate-300">
                        <span
                          className="inline-block h-1.5 rounded-sm bg-cyan-500/60 mr-1.5 align-middle"
                          style={{ width: `${Math.max(det.confidence * 40, 4)}px` }}
                        />
                        {(det.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="text-slate-600 text-[10px]">
                        {det.bbox_xyxy.map(v => Math.round(v)).join(', ')}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* RIGHT PANEL — Image Preview */}
        <div className="xl:col-span-3 flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
            {/* Original */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-lg overflow-hidden flex flex-col">
              <div className="px-3 py-2 border-b border-slate-800 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-600" />
                <span className="text-[9px] uppercase tracking-widest text-slate-600">Original Image</span>
              </div>
              <div className="flex-1 flex items-center justify-center p-4 min-h-[260px]">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Uploaded hull image"
                    className="max-w-full max-h-[480px] object-contain rounded"
                  />
                ) : (
                  <div className="text-center text-slate-700">
                    <ImageIcon className="w-10 h-10 mx-auto mb-2" />
                    <p className="text-[10px] uppercase tracking-widest">No image loaded</p>
                  </div>
                )}
              </div>
            </div>

            {/* Detection Result */}
            <div className="bg-slate-900/40 border border-slate-800 rounded-lg overflow-hidden flex flex-col">
              <div className="px-3 py-2 border-b border-slate-800 flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${result ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`} />
                <span className="text-[9px] uppercase tracking-widest text-slate-600">Detection Overlay</span>
              </div>
              <div className="flex-1 flex items-center justify-center p-4 min-h-[260px]">
                {loading && (
                  <div className="text-center">
                    <ScanLine className="w-8 h-8 mx-auto mb-2 text-cyan-500 animate-pulse" />
                    <p className="text-[10px] text-cyan-400 uppercase tracking-widest animate-pulse">
                      Running YOLOv8 inference...
                    </p>
                  </div>
                )}
                {!loading && result?.annotated_image_base64 && (
                  <img
                    src={`data:image/jpeg;base64,${result.annotated_image_base64}`}
                    alt="Detection result with bounding boxes"
                    className="max-w-full max-h-[480px] object-contain rounded"
                  />
                )}
                {!loading && result && !result.annotated_image_base64 && (
                  <div className="text-center text-slate-700">
                    <CheckCircle className="w-8 h-8 mx-auto mb-2 text-emerald-500" />
                    <p className="text-[10px] uppercase tracking-widest text-emerald-600">No cracks detected</p>
                  </div>
                )}
                {!loading && !result && (
                  <div className="text-center text-slate-700">
                    <ScanLine className="w-10 h-10 mx-auto mb-2" />
                    <p className="text-[10px] uppercase tracking-widest">Run detection to see overlay</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Info card */}
          <div className="bg-slate-900/30 border border-slate-800/60 rounded-lg p-4 grid grid-cols-3 gap-4">
            {[
              { label: 'Model Architecture', value: 'YOLOv8n (nano)', sub: 'Optimized for edge' },
              { label: 'Detection Target', value: 'Hull Cracks', sub: 'Structural surface defects' },
              { label: 'API Endpoint', value: 'localhost:8004', sub: '/predict · POST multipart' },
            ].map(({ label, value, sub }) => (
              <div key={label}>
                <p className="text-[9px] uppercase tracking-widest text-slate-600 mb-0.5">{label}</p>
                <p className="text-xs font-bold text-slate-300">{value}</p>
                <p className="text-[9px] text-slate-600">{sub}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
