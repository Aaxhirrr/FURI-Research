import React, { useEffect, useRef, useState } from "react";
import { Network } from "vis-network";
import { Loader2, RefreshCcw, AlertCircle, Sun, Moon } from "lucide-react";

export function GraphSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [limit, setLimit] = useState(200);
  const [isLightMode, setIsLightMode] = useState(false);
  
  const getNetworkOptions = (light: boolean) => ({
    nodes: {
      shape: "dot",
      size: 20,
      font: { 
        color: light ? "#000000" : "#ffffff", 
        size: 16, 
        strokeWidth: 4,
        strokeColor: light ? "rgba(255, 255, 255, 0.9)" : "rgba(10, 10, 10, 0.9)",
        face: "Inter, sans-serif"
      },
      borderWidth: 2
    },
    edges: {
      width: 1.5,
      font: { 
        color: light ? "#333333" : "#dddddd", 
        size: 14, 
        align: "middle",
        strokeWidth: 4,
        strokeColor: light ? "#ffffff" : "#0a0a0a"
      },
      color: { 
        color: light ? "#cbd5e1" : "#444444", 
        highlight: light ? "#64748b" : "#888888", 
        hover: light ? "#64748b" : "#888888" 
      },
      smooth: true
    },
    physics: {
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -150,
        centralGravity: 0.02,
        springConstant: 0.08,
        springLength: 120,
        damping: 0.4
      },
      stabilization: { iterations: 150 }
    },
    groups: {
      Patient: { color: { background: "#10b981", border: "#059669" } },
      ClinicalState: { color: { background: "#f43f5e", border: "#e11d48" } },
      Biomarker: { color: { background: "#3b82f6", border: "#2563eb" } }
    }
  });

  const loadGraph = async () => {
    if (!containerRef.current) return;
    setLoading(true);
    setError("");
    try {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
      const res = await fetch(`/api/graph?limit=${limit}`);
      if (!res.ok) {
         const err = await res.json();
         throw new Error(err.error || "Failed to fetch Knowledge Graph");
      }
      const data = await res.json();
      
      const options = getNetworkOptions(isLightMode);
      
      if (!containerRef.current) return;
      networkRef.current = new Network(containerRef.current, data, options);
    } catch (e: any) {
      console.error(e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, []);

  // Update visual options dynamically when the user toggles backgrounds
  useEffect(() => {
    if (networkRef.current) {
      networkRef.current.setOptions(getNetworkOptions(isLightMode));
    }
  }, [isLightMode]);

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Global Knowledge Graph</h2>
          <p className="text-muted-foreground">Interactive visualization of the complete FuriMasterKG ontology.</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsLightMode(!isLightMode)}
            className="p-2.5 rounded-lg border border-border bg-card text-foreground hover:bg-muted transition-colors shadow-sm flex items-center justify-center"
            title="Toggle Graph Background"
          >
            {isLightMode ? <Moon className="w-5 h-5 text-primary" /> : <Sun className="w-5 h-5 text-primary" />}
          </button>
          
          <div className="flex items-center gap-3 bg-card border border-border px-4 py-2 rounded-lg shadow-sm">
            <span className="text-sm font-medium text-foreground whitespace-nowrap">Load <span className="text-primary">{limit}</span> Nodes</span>
            <input 
              type="range" min="50" max="1000" step="50" 
              value={limit} onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-28 accent-primary cursor-pointer" 
            />
          </div>
          <button onClick={loadGraph} className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 shadow-sm transition-all">
            <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Fetch Global Graph
          </button>
        </div>
      </div>

      {error ? (
         <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-lg flex items-center gap-3">
           <AlertCircle className="w-5 h-5" />
           <p>{error}</p>
         </div>
      ) : (
        <div 
           className="flex-1 rounded-xl shadow-sm relative overflow-hidden ring-1 ring-border transition-colors duration-500" 
           style={{ backgroundColor: isLightMode ? '#ffffff' : '#0a0a0a' }}
        >
          {loading && (
             <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-10 flex flex-col items-center justify-center text-primary">
               <Loader2 className="w-8 h-8 animate-spin mb-4" />
               <p className="font-semibold">Querying Neo4j Aura Graph...</p>
             </div>
          )}
          <div ref={containerRef} className="w-full h-full" />
        </div>
      )}
    </div>
  );
}
