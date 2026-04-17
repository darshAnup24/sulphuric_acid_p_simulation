<script lang="ts">
  import { onMount } from "svelte";
  import {
    Activity,
    AlertTriangle,
    Zap,
    Cpu,
    Thermometer,
    Gauge,
    Wind,
    Database,
    ShieldCheck,
    AlertOctagon,
    TerminalSquare
  } from "lucide-svelte";
  import { Chart, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from 'chart.js';
  import { Line } from 'svelte-chartjs';

  Chart.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

  // --- STATE ---
  type NodeStatus = "NORMAL" | "WARNING" | "CRITICAL";

  let plantStatus: NodeStatus = "NORMAL";
  
  let reactorTemp = 345;
  let pressure = 2.2;
  let converterFlow = 98;
  let tankLevel = 72;

  let espStatus = {
    reactor: "NORMAL",
    converter: "NORMAL",
    tank: "NORMAL",
  };

  let modelExplanation = {
    severity: "NORMAL",
    area: "-",
    parameter: "-",
    reason: "System is operating within safe parameters.",
    details: "All metrics are stable. Continuous ML monitoring active."
  };

  let simulatedLcdText = "SYSTEM NORMAL\n\n";

  let isOverheating = false;
  let anomalyMode: "NONE" | "REACTOR" | "CONVERTER" | "TANK" = "NONE";
  
  // Charts
  let timeLabels = Array(15).fill("");
  let tempHistory = Array(15).fill(345);
  let timer: any;
  let tick = 0;

  let chartData = {
    labels: timeLabels,
    datasets: [
      {
        label: 'Reactor Temp (°C)',
        fill: true,
        lineTension: 0.3,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3B82F6',
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: 'miter',
        pointBorderColor: '#3B82F6',
        pointBackgroundColor: '#fff',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: '#3B82F6',
        pointHoverBorderColor: 'rgba(220,220,220,1)',
        pointHoverBorderWidth: 2,
        pointRadius: 3,
        pointHitRadius: 10,
        data: tempHistory,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      y: { min: 320, max: 460 },
      x: { display: false }
    },
    plugins: {
      legend: { display: false }
    }
  };

  function updateChart() {
    tempHistory = [...tempHistory.slice(1), reactorTemp];
    chartData = {
      ...chartData,
      datasets: [
        {
          ...chartData.datasets[0],
          data: tempHistory,
          borderColor: plantStatus === "NORMAL" ? '#10B981' : (plantStatus === "WARNING" ? '#F59E0B' : '#EF4444'),
          pointBorderColor: plantStatus === "NORMAL" ? '#10B981' : (plantStatus === "WARNING" ? '#F59E0B' : '#EF4444'),
        }
      ]
    };
  }

  async function fetchState() {
    try {
      const res = await fetch("http://localhost:8000/api/state");
      const data = await res.json();
      
      reactorTemp = data.metrics.reactorTemp;
      pressure = data.metrics.pressure;
      converterFlow = data.metrics.converterFlow;
      tankLevel = data.metrics.tankLevel;
      anomalyMode = data.anomalyMode;
      
      plantStatus = data.eval.status;
      espStatus = data.eval.espStatus;
      simulatedLcdText = data.eval.simulatedLcdText;
      modelExplanation = data.eval.modelExplanation;

      updateChart();
    } catch (e) {
      console.error("Failed to fetch state API", e);
    }
  }

  async function setAnomalyMode(mode) {
    try {
      await fetch("http://localhost:8000/api/anomaly", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode })
      });
    } catch (e) {
      console.error("Failed to trigger anomaly", e);
    }
  }

  function injectReactorOverheating() {
    setAnomalyMode("REACTOR");
  }
  
  function injectConverterBlockage() {
    setAnomalyMode("CONVERTER");
  }

  function injectTankOverflow() {
    setAnomalyMode("TANK");
  }

  function resetSim() {
    setAnomalyMode("NONE");
    tempHistory = Array(15).fill(345);
  }

  onMount(() => {
    timer = setInterval(fetchState, 1000);
    return () => clearInterval(timer);
  });

  // Helpers for UI
  const getSeverityColor = (status: string) => {
    if (status === "NORMAL") return "var(--color-normal)";
    if (status === "WARNING") return "var(--color-warning)";
    if (status === "CRITICAL") return "var(--color-critical)";
    return "#fff";
  };
</script>

<main class="dashboard">
  <header class="top-nav">
    <div class="logo">
      <Activity size={28} color="var(--color-primary)" />
      <h1>Intelligent Plant Monitor</h1>
    </div>
    <div class="status-badge" style="background-color: {getSeverityColor(plantStatus)}22; border: 1px solid {getSeverityColor(plantStatus)}; color: {getSeverityColor(plantStatus)}">
      {#if plantStatus === "NORMAL"}
        <ShieldCheck size={18} />
        <span>System Healthy</span>
      {:else if plantStatus === "WARNING"}
        <AlertTriangle size={18} />
        <span>Warning Detected</span>
      {:else}
        <AlertOctagon size={18} />
        <span>Critical State</span>
      {/if}
    </div>
  </header>

  <div class="content-grid">
    <!-- COLUMN 1: Simulation View -->
    <div class="col-left">
      <section class="glass-panel panel-large">
        <div class="panel-header">
          <h2><Zap size={20} /> Plant Simulation View</h2>
        </div>
        
        <div class="metrics-grid">
          <div class="metric-card" class:warning={anomalyMode==="REACTOR" && plantStatus==="WARNING"} class:critical={anomalyMode==="REACTOR" && plantStatus==="CRITICAL"}>
            <div class="metric-icon"><Thermometer size={24} /></div>
            <div class="metric-data">
              <span class="label">Reactor Temp</span>
              <span class="value mono">{reactorTemp}<span class="unit">°C</span></span>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon"><Gauge size={24} /></div>
            <div class="metric-data">
              <span class="label">Pressure</span>
              <span class="value mono">{pressure}<span class="unit">bar</span></span>
            </div>
          </div>
          
          <div class="metric-card" class:warning={anomalyMode==="CONVERTER" && plantStatus==="WARNING"} class:critical={anomalyMode==="CONVERTER" && plantStatus==="CRITICAL"}>
            <div class="metric-icon"><Wind size={24} /></div>
            <div class="metric-data">
              <span class="label">Converter Flow</span>
              <span class="value mono">{converterFlow}<span class="unit">Nm³/h</span></span>
            </div>
          </div>
          
          <div class="metric-card" class:warning={anomalyMode==="TANK" && plantStatus==="WARNING"} class:critical={anomalyMode==="TANK" && plantStatus==="CRITICAL"}>
            <div class="metric-icon"><Database size={24} /></div>
            <div class="metric-data">
              <span class="label">Tank Level</span>
              <span class="value mono">{tankLevel}<span class="unit">%</span></span>
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3 class="chart-title">Reactor Temperature Trend</h3>
          <div class="chart-wrapper">
             <Line data={chartData} options={chartOptions} />
          </div>
        </div>

        <div class="lcd-mock">
          <div class="lcd-screen mono">
            <pre>{simulatedLcdText}</pre>
          </div>
        </div>

      </section>
    </div>

    <!-- COLUMN 2: AI, Nodes & Actions -->
    <div class="col-right">
      
      <!-- ESP Nodes -->
      <section class="glass-panel panel-nodes">
        <div class="panel-header">
          <h2><TerminalSquare size={20} /> ESP Node Status</h2>
        </div>
        <div class="node-list">
          <div class="node-item">
            <div class="node-info">
               <Cpu size={20} />
               <span>Reactor Node</span>
            </div>
            <div class="led-state">
               <div class="led" style="background-color: {getSeverityColor(espStatus.reactor)}; box-shadow: 0 0 10px {getSeverityColor(espStatus.reactor)}"></div>
               <span class="status-text mono" style="color: {getSeverityColor(espStatus.reactor)}">{espStatus.reactor}</span>
            </div>
          </div>
          <div class="node-item">
            <div class="node-info">
               <Cpu size={20} />
               <span>Converter Node</span>
            </div>
            <div class="led-state">
               <div class="led" style="background-color: {getSeverityColor(espStatus.converter)}; box-shadow: 0 0 10px {getSeverityColor(espStatus.converter)}"></div>
               <span class="status-text mono" style="color: {getSeverityColor(espStatus.converter)}">{espStatus.converter}</span>
            </div>
          </div>
          <div class="node-item">
            <div class="node-info">
               <Cpu size={20} />
               <span>Tank Node</span>
            </div>
            <div class="led-state">
               <div class="led" style="background-color: {getSeverityColor(espStatus.tank)}; box-shadow: 0 0 10px {getSeverityColor(espStatus.tank)}"></div>
               <span class="status-text mono" style="color: {getSeverityColor(espStatus.tank)}">{espStatus.tank}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ML Alert Panel -->
      <section class="glass-panel panel-ml">
        <div class="panel-header">
          <h2><Activity size={20} /> ML Anomaly Explanation</h2>
        </div>
        <div class="explanation-box" style="border-left: 4px solid {getSeverityColor(modelExplanation.severity)}">
          <div class="explanation-header">
            <span class="badge" style="background-color: {getSeverityColor(modelExplanation.severity)}">
              {modelExplanation.severity}
            </span>
            <span class="area">Area: <strong>{modelExplanation.area}</strong></span>
          </div>
          <div class="explanation-body">
            <p><strong>Parameter:</strong> {modelExplanation.parameter}</p>
            <p><strong>Reason:</strong> {modelExplanation.reason}</p>
            <div class="details-box">
              <pre>{modelExplanation.details}</pre>
            </div>
          </div>
        </div>
      </section>

      <!-- Controls -->
      <section class="glass-panel panel-controls">
        <div class="panel-header">
          <h2><Zap size={20} /> Inject Anomalies</h2>
        </div>
        <div class="buttons-grid">
          <button class="btn btn-warning" disabled={anomalyMode!=="NONE"} on:click={injectReactorOverheating}>
            Inject Reactor Overheating
          </button>
          <button class="btn btn-warning" disabled={anomalyMode!=="NONE"} on:click={injectConverterBlockage}>
             Inject Converter Blockage
          </button>
          <button class="btn btn-warning" disabled={anomalyMode!=="NONE"} on:click={injectTankOverflow}>
             Inject Tank Overflow
          </button>
          <button class="btn btn-normal" on:click={resetSim}>
             Reset to Normal
          </button>
        </div>
      </section>

    </div>
  </div>
</main>

<style>
  .dashboard {
    min-height: 100vh;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card-bg);
    padding: 1rem 1.5rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .logo h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #3B82F6, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 1.5rem;
    flex: 1;
  }

  .panel-header {
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 0.75rem;
  }
  
  .panel-header h2 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.2rem;
    margin: 0;
    color: var(--text-main);
  }

  section {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
  }

  .col-left, .col-right {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .panel-large {
    flex: 1;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .metric-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s;
  }

  .metric-card.warning {
    border-color: var(--color-warning);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
  }
  
  .metric-card.critical {
    border-color: var(--color-critical);
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
    animation: pulseRed 1.5s infinite alternate;
  }

  @keyframes pulseRed {
    from { background: rgba(239, 68, 68, 0.05); }
    to { background: rgba(239, 68, 68, 0.2); }
  }

  .metric-icon {
    background: rgba(255,255,255,0.05);
    padding: 0.75rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .metric-data {
    display: flex;
    flex-direction: column;
  }

  .metric-data .label {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .metric-data .value {
    font-size: 1.7rem;
    font-weight: 700;
  }

  .metric-data .unit {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-left: 0.2rem;
  }

  .chart-container {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 2rem;
  }

  .chart-title {
    font-size: 1rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .chart-wrapper {
    height: 180px;
    position: relative;
  }

  .lcd-mock {
    background: #111;
    border: 4px solid #333;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: inset 0 0 20px rgba(0,0,0,1);
  }

  .lcd-screen {
    background: #00FF41;
    background: linear-gradient(180deg, #0f380f 0%, #306230 100%);
    color: #8bac0f;
    padding: 1rem;
    border-radius: 4px;
    font-size: 1.2rem;
    font-weight: 700;
    text-shadow: 1px 1px 0px rgba(0,0,0,0.5);
    min-height: 80px;
    display: flex;
    align-items: center;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
  }

  .lcd-screen pre {
    margin: 0;
    white-space: pre-wrap;
  }

  /* Node List */
  .node-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .node-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,0.2);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.05);
  }

  .node-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 500;
  }

  .led-state {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .led {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    transition: all 0.3s;
  }

  /* ML Explanation */
  .explanation-box {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 1rem;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .explanation-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .explanation-header .badge {
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }

  .explanation-body p {
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
  }

  .details-box {
    margin-top: 1rem;
    background: rgba(0,0,0,0.3);
    padding: 1rem;
    border-radius: 6px;
    font-size: 0.9rem;
    border: 1px solid rgba(255,255,255,0.05);
  }
  
  .details-box pre {
    white-space: pre-wrap;
    font-family: inherit;
    margin: 0;
  }

  /* Controls */
  .buttons-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .btn {
    padding: 0.75rem 1rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s;
    color: #fff;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-warning {
    background: transparent;
    border: 1px solid var(--color-warning);
    color: var(--color-warning);
  }

  .btn-warning:hover:not(:disabled) {
    background: rgba(245, 158, 11, 0.1);
  }

  .btn-normal {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--color-normal);
    color: var(--color-normal);
    grid-column: span 2;
  }
  
  .btn-normal:hover:not(:disabled) {
    background: rgba(16, 185, 129, 0.2);
  }

  @media (max-width: 1024px) {
    .content-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
