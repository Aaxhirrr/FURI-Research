"use client";

import { useState, useEffect } from "react";
import { MetricCard } from "@/components/dashboard/metric-card";
import { Users, Droplet, Activity, Network, Loader2, AlertCircle, Play } from "lucide-react";

export function OverviewSection({ rid }: { rid?: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [evalLoading, setEvalLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<any>(null);

  useEffect(() => {
    if (!rid) return;
    const fetchData = async () => {
      setLoading(true);
      setError("");
      setEvaluation(null); // Reset eval on new RID
      try {
        const res = await fetch(`/api/patient/${rid}`);
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.error || "Patient not found in Neo4j Knowledge Graph.");
        }
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        setError(err.message);
        setData(null);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [rid]);

  const runEval = async () => {
    setEvalLoading(true);
    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rid })
      });
      const resData = await res.json();
      if (!res.ok) throw new Error(resData.error || "Evaluation failed");
      setEvaluation(resData);
    } catch (e: any) {
      alert("Failed to run models: " + e.message);
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* 1. The Top Row: KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Processed"
          value="1,730"
          change="Active Patient Nodes"
          changeType="positive"
          icon={Users}
          delay={0}
        />
        <MetricCard
          title="Conversion Rate"
          value="46.0%"
          change="MCI-to-Dementia over 4.1 yrs"
          changeType="positive"
          icon={Activity}
          delay={1}
        />
        <MetricCard
          title="Atrophy Velocity"
          value="3.9%"
          change="Annual Hippocampal Loss"
          changeType="negative"
          icon={Droplet}
          delay={2}
        />
        <MetricCard
          title="Graph Edges"
          value="1,204"
          change="P2P Clinical Twins Mapped"
          changeType="positive"
          icon={Network}
          delay={3}
        />
      </div>

      {/* 2. Middle Section: The Patient Explorer */}
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden min-h-[16rem]">
        <div className="bg-muted/30 border-b border-border px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
            Patient Timeline: <span className="text-primary tracking-wider">RID {rid}</span>
          </h2>
          
          {loading && (
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <Loader2 className="w-4 h-4 animate-spin" /> Querying Graph...
            </div>
          )}
          {!loading && !error && data && (
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 px-3 py-1 rounded-full text-sm font-medium animate-in zoom-in duration-300">
              <Network className="w-4 h-4" />
              Graph Connected: Matches {data.twinsCount || 0} Clinical Twins
            </div>
          )}
        </div>
        
        <div className="p-6">
          {loading ? (
             <div className="flex items-center justify-center h-32 text-muted-foreground">
               Fetching trajectory from FuriMasterKG...
             </div>
          ) : error ? (
             <div className="bg-destructive/10 border border-destructive/20 text-destructive p-4 rounded-lg flex items-center gap-3">
               <AlertCircle className="w-5 h-5" />
               <p>{error}</p>
             </div>
          ) : (
             <div className="bg-background rounded-lg border border-border p-4 max-h-[18rem] overflow-y-auto text-sm leading-relaxed text-muted-foreground shadow-inner whitespace-pre-wrap">
               {data?.summary}
             </div>
          )}
        </div>
      </div>

      {/* 3. Bottom Section: The FURI Arena */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold tracking-tight flex items-center gap-2">
            Architecture Evaluation: <span className="text-muted-foreground font-normal">The "Memory" Test</span>
          </h3>
          <button 
            onClick={runEval} 
            disabled={evalLoading || !data || !!error} 
            className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {evalLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {evalLoading ? "Running Gemini 2.5 Pipeline..." : "Trigger Live Baseline Evaluation"}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
          
          {/* C0 Stateless Model */}
          <div className="flex flex-col border border-border rounded-xl overflow-hidden bg-card shadow-sm transition-all hover:shadow-md">
            <div className="bg-rose-500/5 border-b border-border p-4 flex flex-col gap-2">
              <h4 className="font-semibold text-foreground text-lg">Model C0 (Stateless Baseline)</h4>
              <div className="inline-flex max-w-fit items-center text-xs font-mono bg-rose-500/10 text-rose-600 dark:text-rose-400 px-2.5 py-1 rounded-md">
                [Context Injected: ONLY Latest Visit]
              </div>
            </div>
            <div className="p-5 flex-1 flex flex-col">
              <div className="bg-muted/40 flex-1 rounded-lg p-4 font-mono text-sm border border-border/50 mb-4 whitespace-pre-wrap h-[16rem] overflow-y-auto">
                {evaluation ? (
                  <span className="text-muted-foreground animate-in fade-in">{evaluation.c0_output}</span>
                ) : (
                  <span className="text-muted-foreground/50 italic flex h-full items-center justify-center">Awaiting evaluation pipeline trigger...</span>
                )}
              </div>
              <div className="bg-rose-500 text-white font-medium px-4 py-2.5 rounded-lg text-center flex items-center justify-center gap-2 shadow-sm">
                ❌ Expected Outcome: Insufficient Temporal Context
              </div>
            </div>
          </div>

          {/* C1 Memory Model */}
          <div className="flex flex-col border border-border rounded-xl overflow-hidden bg-card shadow-sm transition-all hover:shadow-md">
            <div className="bg-emerald-500/5 border-b border-border p-4 flex flex-col gap-2">
              <h4 className="font-semibold text-foreground text-lg">Model C1 (Memory Augmented)</h4>
              <div className="inline-flex max-w-fit items-center text-xs font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-1 rounded-md">
                [Context Injected: Full Episodic Timeline]
              </div>
            </div>
            <div className="p-5 flex-1 flex flex-col">
              <div className="bg-muted/40 flex-1 rounded-lg p-4 font-mono text-sm border border-border/50 mb-4 whitespace-pre-wrap h-[16rem] overflow-y-auto">
                {evaluation ? (
                  <span className="text-foreground animate-in fade-in">{evaluation.c1_output}</span>
                ) : (
                  <span className="text-muted-foreground/50 italic flex h-full items-center justify-center">Awaiting evaluation pipeline trigger...</span>
                )}
              </div>
              <div className="bg-emerald-500 text-white font-medium px-4 py-2.5 rounded-lg text-center flex items-center justify-center gap-2 shadow-sm">
                ✅ Expected Outcome: Trajectory Successfully Mapped
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
