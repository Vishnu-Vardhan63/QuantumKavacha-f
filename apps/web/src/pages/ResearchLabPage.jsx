import React, { useState } from 'react';
import { Atom, Play, CheckCircle2, AlertCircle, Cpu } from 'lucide-react';

export default function ResearchLabPage() {
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [running, setRunning] = useState(false);

  const handleRunBenchmark = () => {
    setRunning(true);
    fetch('/api/quantum/benchmark')
      .then(res => res.json())
      .then(data => {
        setBenchmarkResult(data);
        setRunning(false);
      })
      .catch(() => setRunning(false));
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Quantum Research Lab</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Experimental Qiskit circuit routines, Pauli feature mapping, and quantum kernel benchmarking.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Benchmark Control Panel */}
        <div className="qk-panel" style={{ padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={18} color="var(--accent-cyan)" /> Qiskit Kernel Simulator
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
            Executes a 4-qubit Second-Order Pauli Expansion (ZZFeatureMap) circuit to benchmark quantum state fidelity against classical distance metrics.
          </p>

          <button 
            className="btn-primary" 
            onClick={handleRunBenchmark}
            disabled={running}
            style={{ opacity: running ? 0.7 : 1 }}
          >
            <Play size={15} /> {running ? 'Simulating Quantum Circuit...' : 'Run Quantum Benchmark'}
          </button>
        </div>

        {/* Status Card */}
        <div className="qk-panel" style={{ padding: '1.75rem', background: '#0F1A28' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
            Hardware & Simulation Boundary
          </h3>
          <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <li>Quantum state vectors are evaluated via Qiskit 2.x local primitives.</li>
            <li>Production fraud verdicts do NOT depend on experimental quantum simulation.</li>
            <li>Zero fabricated quantum supremacy benchmarks; all metrics reflect local simulator timings.</li>
          </ul>
        </div>
      </div>

      {benchmarkResult && (
        <div className="qk-panel" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={18} color="#10B981" /> Benchmark Results
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'var(--surface-secondary)', padding: '1rem', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Circuit Type</div>
              <strong style={{ fontSize: '0.9rem' }}>{benchmarkResult.circuit_type}</strong>
            </div>
            <div style={{ background: 'var(--surface-secondary)', padding: '1rem', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Qubit Count / Depth</div>
              <strong style={{ fontSize: '0.9rem' }}>{benchmarkResult.qubit_count} qubits (depth: {benchmarkResult.circuit_depth})</strong>
            </div>
            <div style={{ background: 'var(--surface-secondary)', padding: '1rem', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Simulation Latency</div>
              <strong style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>{benchmarkResult.execution_latency_ms} ms</strong>
            </div>
          </div>

          <div style={{ background: '#0B1320', padding: '1rem', borderRadius: '6px', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
            <pre style={{ margin: 0, color: 'var(--text-crisp-white)' }}>
              {JSON.stringify(benchmarkResult, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
