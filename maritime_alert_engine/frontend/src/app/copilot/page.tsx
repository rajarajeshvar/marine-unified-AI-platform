'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import './copilot.css';

// ─── Types ───

type Source = {
  source_file: string;
  document_type: string;
  page: string;
  equipment_hint: string;
};

type Message = {
  id: string;
  role: 'user' | 'ai';
  content: string;
  sources?: Source[];
};

type SensorData = {
  timestamp: string;
  engine_rpm: number;
  temperature_c: number;
  oil_pressure_bar: number;
  fuel_pressure_bar: number;
  cooling_water_temp_c: number;
  vibration_mm_s: number;
  engine_load_pct: number;
  lube_oil_temp_c: number;
  exhaust_temp_c: number;
  fuel_consumption: number;
  fault_label: string;
};

type Alarm = {
  timestamp: string;
  fault_label: string;
  rpm: number;
  temperature: number;
  vibration: number;
};

type Prediction = {
  failure_probability: number;
  remaining_useful_life_hours: number;
  risk_level: string;
  predicted_fault: string;
  risk_factors: string[];
};

type MaintenanceRecord = {
  date: string;
  equipment: string;
  fault: string;
  action_taken: string;
  severity: string;
  equipment_type?: string;
  fault_code?: string;
  maintenance_type?: string;
  downtime_hours?: number;
  status?: string;
};

// ─── Component ───

export default function CopilotPage() {
  // Core state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [sensorData, setSensorData] = useState<SensorData | null>(null);
  const [predictions, setPredictions] = useState<Prediction | null>(null);
  const [activeAlarms, setActiveAlarms] = useState<Alarm[]>([]);
  const [sessionId] = useState(() => `session_${Math.random().toString(36).substr(2, 9)}`);

  // UI state
  const [selectedEngine, setSelectedEngine] = useState('Engine 2');
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline'>('offline');
  const [maintenanceHistory, setMaintenanceHistory] = useState<MaintenanceRecord[]>([]);
  const [showEvents, setShowEvents] = useState(true);
  const [sourcesVisible, setSourcesVisible] = useState<Record<string, boolean>>({});
  const [evidenceVisible, setEvidenceVisible] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [snapshotTime, setSnapshotTime] = useState<string>('');

  // ── FIX #1: Telemetry consistency ──
  // After a /chat response, the dashboard must freeze to that snapshot.
  // We track the last chat response time; polling is suppressed for 30s after chat.
  const chatSnapshotLockUntil = useRef<number>(0);

  // ─── Data Fetching ───

  const fetchDashboard = useCallback(async () => {
    // If we're within the chat-snapshot lock window, skip the poll
    // so the dashboard values stay consistent with the last chat response.
    if (Date.now() < chatSnapshotLockUntil.current) return;

    try {
      const res = await fetch('http://localhost:8005/sensors');
      if (res.ok) {
        const data = await res.json();
        setSensorData(data.sensor_data);
        setPredictions(data.predictions);
        setActiveAlarms(data.active_alarms);
        setBackendStatus('online');
        setSnapshotTime(new Date().toLocaleTimeString());
      } else {
        setBackendStatus('offline');
      }
    } catch {
      setBackendStatus('offline');
    }
  }, []);

  const fetchMaintenance = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8005/maintenance?limit=5');
      if (res.ok) {
        const data = await res.json();
        setMaintenanceHistory(data.maintenance_history || []);
      }
    } catch {
      /* silent */
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    fetchMaintenance();
    const interval = setInterval(fetchDashboard, 10000);
    return () => clearInterval(interval);
  }, [fetchDashboard, fetchMaintenance]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ─── Chat Handler ───

  const sendMessage = async (text: string) => {
    const userMsg = text.trim();
    if (!userMsg || isLoading) return;

    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8005/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: data.response,
        sources: data.sources,
      }]);

      // FIX #1: Use the SAME sensor snapshot from the /chat response
      // and lock the polling for 30 seconds so it doesn't overwrite.
      setSensorData(data.sensor_data);
      setPredictions(data.predictions);
      setActiveAlarms(data.active_alarms);
      setBackendStatus('online');
      setSnapshotTime(new Date().toLocaleTimeString());
      chatSnapshotLockUntil.current = Date.now() + 30000; // 30s lock

      fetchMaintenance();
    } catch {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: '⚠ Unable to connect to the Engineering Copilot. Check that the backend and Ollama service are running.',
      }]);
      setBackendStatus('offline');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  // ─── Helpers ───

  const getUniqueSources = (sources: Source[]) => {
    if (!sources) return [];
    const unique = new Map<string, Source>();
    sources.forEach(src => {
      if (!unique.has(src.source_file)) unique.set(src.source_file, src);
    });
    return Array.from(unique.values());
  };

  const toggleSources = (msgId: string) => {
    setSourcesVisible(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const toggleEvidence = (msgId: string) => {
    setEvidenceVisible(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const copyToClipboard = (text: string, msgId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getSourceIcon = (src: Source) => {
    const dt = (src.document_type || '').toLowerCase();
    const fn = (src.source_file || '').toLowerCase();
    if (dt === 'sop' || dt === 'manual' || fn.endsWith('.pdf')) return '📘';
    if (fn.endsWith('.csv')) return '🛠';
    return '📄';
  };

  const formatPageInfo = (src: Source) => {
    const p = src.page;
    if (!p || p === 'N/A' || p === 'None' || p === 'null') return null;
    return `Page ${p}`;
  };

  const getEventLabel = () => {
    if (maintenanceHistory.length === 0) return 'Recent Events';
    const hasMaintAction = maintenanceHistory.some(r =>
      r.maintenance_type === 'Preventive' ||
      r.maintenance_type === 'Scheduled' ||
      (r.action_taken && r.action_taken.toLowerCase().includes('replaced')) ||
      (r.action_taken && r.action_taken.toLowerCase().includes('overhauled'))
    );
    return hasMaintAction ? 'Recent Maintenance' : 'Recent Events';
  };

  const autoResizeTextarea = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
    }
  };

  const hasConversation = messages.length > 0;
  const telemetryConnected = sensorData !== null;

  const quickActions = [
    'Why is Engine 2 critical?',
    'Check engine status',
    'Show active alarms',
    'Find overheating SOP',
    'Analyze vibration',
    'Check maintenance history',
  ];

  const engines = [
    { name: 'Engine 1', id: 'Engine 1' },
    { name: 'Engine 2', id: 'Engine 2' },
    { name: 'Engine 3', id: 'Engine 3' },
  ];

  // ─── Render ───

  return (
    <div className="copilot-theme">
      <div className="app-shell">
        {/* ═══ TOP HEADER ═══ */}
        <header className="top-header">
          <div className="header-brand">
            <span className="brand-anchor">⚓</span>
            <div>
              <h1>Marine Engineering Copilot</h1>
              <div className="header-subtitle">AI Engineering Decision Support</div>
            </div>
          </div>
          <div className="header-status-group">
            <a href="/" style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginRight: '1rem', textDecoration: 'none', borderBottom: '1px solid transparent' }}>← Back to Dashboard</a>
            <span className={`status-pill ${backendStatus === 'online' ? 'online' : 'offline'}`}>
              <span className={`status-dot ${backendStatus === 'online' ? 'green' : 'red'}`} />
              {backendStatus === 'online' ? 'AI Online' : 'AI Offline'}
            </span>
            <span className={`status-pill ${backendStatus === 'online' ? 'online' : 'offline'}`}>
              <span className={`status-dot ${backendStatus === 'online' ? 'green' : 'red'}`} />
              Knowledge Base {backendStatus === 'online' ? 'Ready' : 'Offline'}
            </span>
            <span className={`status-pill ${telemetryConnected ? 'online' : 'offline'}`}>
              <span className={`status-dot ${telemetryConnected ? 'green' : 'red'}`} />
              Telemetry {telemetryConnected ? 'Connected' : 'Offline'}
            </span>
          </div>
        </header>

        {/* ═══ LEFT SIDEBAR ═══ */}
        <aside className="left-sidebar">
          {/* Engine Fleet */}
          <div className="sidebar-section">
            <div className="section-label">Engine Fleet</div>
            <div className="engine-list">
              {engines.map(eng => (
                <div
                  key={eng.id}
                  className={`engine-item ${selectedEngine === eng.id ? 'selected' : ''}`}
                  onClick={() => setSelectedEngine(eng.id)}
                >
                  <span className="engine-dot" />
                  <span className="engine-name">{eng.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Active Alarms */}
          <div className="sidebar-section">
            <div className="section-label">Active Alarms</div>
            {activeAlarms && activeAlarms.length > 0 ? (
              <div className="alarm-list">
                {activeAlarms.map((a, i) => (
                  <div
                    key={i}
                    className="alarm-card"
                    onClick={() => {
                      const query = `Why is there a ${a.fault_label} alarm?`;
                      setInput(query);
                      textareaRef.current?.focus();
                    }}
                    title="Click to investigate in chat"
                  >
                    <div className="alarm-fault">🚨 {a.fault_label}</div>
                    <div className="alarm-meta">Detected: {a.timestamp}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-alarms">
                <span className="check-icon">✓</span>
                No active alarms
              </div>
            )}
          </div>

          {/* Recent Events / Recent Maintenance */}
          <div className="sidebar-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
              <div className="section-label" style={{ marginBottom: 0 }}>{getEventLabel()}</div>
              <button className="section-toggle" onClick={() => setShowEvents(!showEvents)}>
                {showEvents ? 'Hide' : 'Show'}
              </button>
            </div>
            {showEvents && (
              maintenanceHistory.length > 0 ? (
                <div className="maint-list">
                  {maintenanceHistory.slice(0, 4).map((rec, i) => (
                    <div key={i} className="maint-item">
                      <div className="maint-desc">{rec.fault}</div>
                      <div className="maint-meta">
                        {rec.equipment} · {formatDate(rec.date)}
                        {rec.severity && rec.severity !== 'N/A' && (
                          <span className={`severity-tag ${rec.severity.toLowerCase()}`}> · {rec.severity}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-data-msg">No recent records</div>
              )
            )}
          </div>
        </aside>

        {/* ═══ CENTER CHAT ═══ */}
        <main className="center-chat">
          {!hasConversation ? (
            <div className="empty-state">
              <div className="empty-anchor">⚓</div>
              <h2>Marine Engineering Copilot</h2>
              <p className="empty-desc">
                Your AI assistant for vessel maintenance and operations.
              </p>
              <div className="capabilities-list">
                <div className="cap-item"><span className="cap-icon">📘</span> Maintenance procedures &amp; SOPs</div>
                <div className="cap-item"><span className="cap-icon">📊</span> Live telemetry analysis</div>
                <div className="cap-item"><span className="cap-icon">🚨</span> Active alarm investigation</div>
                <div className="cap-item"><span className="cap-icon">🤖</span> Failure predictions &amp; risk</div>
                <div className="cap-item"><span className="cap-icon">🛠</span> Maintenance history lookup</div>
              </div>
              <div className="quick-actions">
                {quickActions.map((q, i) => (
                  <button key={i} className="quick-btn" onClick={() => sendMessage(q)}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="chat-messages">
              {messages.map(msg => (
                <div key={msg.id} className={`msg-row ${msg.role}`}>
                  <div className="msg-bubble">
                    {msg.role === 'ai' && (
                      <div className="ai-label">⚓ Engineering Copilot</div>
                    )}
                    {msg.role === 'ai' ? (
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                      msg.content
                    )}
                  </div>

                  {/* Message Actions */}
                  {msg.role === 'ai' && !msg.content.startsWith('⚠') && (
                    <div className="msg-actions">
                      <button
                        className="msg-action-btn"
                        onClick={() => copyToClipboard(msg.content, msg.id)}
                      >
                        {copiedId === msg.id ? '✓ Copied' : 'Copy'}
                      </button>
                      {msg.sources && msg.sources.length > 0 && (
                        <>
                          <button
                            className={`msg-action-btn ${sourcesVisible[msg.id] ? 'active' : ''}`}
                            onClick={() => toggleSources(msg.id)}
                          >
                            {sourcesVisible[msg.id] ? 'Hide Sources' : 'Show Sources'}
                          </button>
                          <button
                            className={`msg-action-btn ${evidenceVisible[msg.id] ? 'active' : ''}`}
                            onClick={() => toggleEvidence(msg.id)}
                          >
                            {evidenceVisible[msg.id] ? 'Hide Evidence' : 'Show Evidence'}
                          </button>
                        </>
                      )}
                    </div>
                  )}

                  {/* Source Display */}
                  {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && sourcesVisible[msg.id] && (
                    <div className="sources-panel">
                      <div className="sources-header">Sources Used</div>
                      <div className="sources-list">
                        {getUniqueSources(msg.sources).map((src, i) => (
                          <div key={i} className="source-card">
                            <span className="src-icon">{getSourceIcon(src)}</span>
                            <div className="src-info">
                              <div className="src-name">{src.source_file}</div>
                              <div className="src-detail-row">
                                {formatPageInfo(src) && (
                                  <span className="src-detail">{formatPageInfo(src)}</span>
                                )}
                                {src.equipment_hint && src.equipment_hint !== 'N/A' && (
                                  <span className="src-detail">Equipment: {src.equipment_hint}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Evidence Display */}
                  {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && evidenceVisible[msg.id] && (
                    <div className="evidence-panel">
                      <div className="evidence-header">📘 Source Evidence</div>
                      <div className="evidence-list">
                        {getUniqueSources(msg.sources).map((src, i) => (
                          <div key={i} className="evidence-card">
                            <div className="evidence-source-name">
                              <span className="src-icon">{getSourceIcon(src)}</span>
                              {src.source_file}
                            </div>
                            {formatPageInfo(src) && (
                              <div className="evidence-page">{formatPageInfo(src)}</div>
                            )}
                            <div className="evidence-body">
                              <div className="evidence-section-label">Supports</div>
                              <div className="evidence-section-text">
                                {src.document_type === 'SOP' || src.document_type === 'manual'
                                  ? 'Referenced in the engineering assessment above'
                                  : src.document_type === 'maintenance_log'
                                    ? 'Maintenance record supporting equipment history'
                                    : 'Retrieved document supporting the response'}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {/* Loading State */}
              {isLoading && (
                <div className="msg-row ai">
                  <div className="loading-indicator">
                    <div className="loading-spinner" />
                    <div className="loading-text">
                      <div className="loading-label">⚓ Copilot is analyzing...</div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Chat Input */}
          <div className="chat-input-area">
            <form onSubmit={handleSubmit} className="input-form">
              <textarea
                ref={textareaRef}
                className="chat-textarea"
                value={input}
                onChange={(e) => { setInput(e.target.value); autoResizeTextarea(); }}
                onKeyDown={handleKeyDown}
                placeholder="Ask about engines, procedures, alarms or maintenance..."
                disabled={isLoading}
                rows={1}
                autoFocus
              />
              <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
                {isLoading ? 'Analyzing...' : 'Send ➤'}
              </button>
            </form>
          </div>
        </main>

        {/* ═══ RIGHT SIDEBAR ═══ */}
        <aside className="right-sidebar">
          {telemetryConnected && sensorData ? (
            <>
              {/* Live Engine Status */}
              <div className="right-section">
                <div className="right-section-header">
                  <span className="right-section-title">Live Engine Status</span>
                  <span className="engine-tag">{selectedEngine}</span>
                </div>
                <div className="telemetry-status">
                  <span className="status-dot green" />
                  Telemetry Connected
                  {snapshotTime && (
                    <span className="snapshot-time">· Updated {snapshotTime}</span>
                  )}
                </div>
                <div className="sensor-grid">
                  <div className="sensor-card">
                    <div className="sensor-label">RPM</div>
                    <div className="sensor-value">
                      {sensorData.engine_rpm}<span className="sensor-unit"> rpm</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Load</div>
                    <div className="sensor-value">
                      {sensorData.engine_load_pct}<span className="sensor-unit"> %</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Engine Temp</div>
                    <div className="sensor-value">
                      {sensorData.temperature_c}<span className="sensor-unit"> °C</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Coolant Temp</div>
                    <div className="sensor-value">
                      {sensorData.cooling_water_temp_c}<span className="sensor-unit"> °C</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Oil Pressure</div>
                    <div className="sensor-value">
                      {sensorData.oil_pressure_bar}<span className="sensor-unit"> bar</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Vibration</div>
                    <div className="sensor-value">
                      {sensorData.vibration_mm_s}<span className="sensor-unit"> mm/s</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Fuel Pressure</div>
                    <div className="sensor-value">
                      {sensorData.fuel_pressure_bar}<span className="sensor-unit"> bar</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Exhaust Temp</div>
                    <div className="sensor-value">
                      {sensorData.exhaust_temp_c}<span className="sensor-unit"> °C</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Lube Oil Temp</div>
                    <div className="sensor-value">
                      {sensorData.lube_oil_temp_c}<span className="sensor-unit"> °C</span>
                    </div>
                  </div>
                  <div className="sensor-card">
                    <div className="sensor-label">Fuel Consumption</div>
                    <div className="sensor-value">
                      {sensorData.fuel_consumption}<span className="sensor-unit"> L/h</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Prediction */}
              {predictions && (
                <div className="right-section">
                  <div className="right-section-header">
                    <span className="right-section-title">AI Prediction</span>
                    <span className={`risk-badge ${predictions.risk_level.toLowerCase()}`}>
                      {predictions.risk_level}
                    </span>
                  </div>
                  <div className="pred-grid">
                    <div className="pred-row">
                      <span className="pred-label">Failure Probability</span>
                      <span className="pred-value">{(predictions.failure_probability * 100).toFixed(1)}%</span>
                    </div>
                    <div className="pred-row">
                      <span className="pred-label">Remaining Useful Life</span>
                      <span className="pred-value">{predictions.remaining_useful_life_hours} hrs</span>
                    </div>
                    <div className="pred-row">
                      <span className="pred-label">Predicted Fault</span>
                      <span className="pred-value" style={{ fontSize: '0.75rem' }}>
                        {predictions.predicted_fault === 'Normal' ? 'None detected' : predictions.predicted_fault}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="connecting-placeholder">
              <div className="loading-spinner" />
              <div>Connecting to telemetry...</div>
            </div>
          )}

          {/* Demo Data Indicator */}
          <div className="demo-badge">
            ◆ SIMULATED · DEMO DATA
          </div>
        </aside>
      </div>
    </div>
  );
}
