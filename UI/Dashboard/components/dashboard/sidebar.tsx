"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import {
  BrainCircuit,
  Search,
  Database,
  LayoutDashboard,
  Network,
  MessageSquare
} from "lucide-react";

export function Sidebar({ onRidSubmit, activeTab, onTabChange, rid }: any) {
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border flex flex-col w-[300px]">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-sidebar-border shrink-0">
        <div className="flex items-center gap-3 w-full">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 bg-primary/10">
            <BrainCircuit className="w-5 h-5 text-primary animate-pulse" />
          </div>
          <span className="font-bold text-lg text-sidebar-foreground whitespace-nowrap">
            FURI Master
          </span>
        </div>
      </div>

      {/* Controls & Nav */}
      <div className="flex-1 p-4 space-y-6 overflow-y-auto flex flex-col">
        {/* Navigation Tabs */}
        <div className="space-y-1">
           <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider pl-3 mb-2 block">
              Application Modules
           </label>
           <button onClick={() => onTabChange('evaluate')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition", activeTab === 'evaluate' ? "bg-sidebar-accent text-sidebar-foreground" : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground")}>
              <LayoutDashboard className="w-4 h-4" /> Timeline Evaluation
           </button>
           <button onClick={() => onTabChange('graph')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition", activeTab === 'graph' ? "bg-sidebar-accent text-sidebar-foreground" : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground")}>
              <Network className="w-4 h-4" /> Global Knowledge Graph
           </button>
           <button onClick={() => onTabChange('consult')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition", activeTab === 'consult' ? "bg-sidebar-accent text-sidebar-foreground" : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground")}>
              <MessageSquare className="w-4 h-4" /> Predictive Consultant
           </button>
        </div>

        {/* Patient Selector */}
        <div className="space-y-2 pt-4 border-t border-sidebar-border/50">
          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider pl-1">
            Active Patient ID
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={rid}
              onChange={(e) => onRidSubmit(e.target.value)}
              placeholder="Search RID (e.g. 4022)"
              className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-foreground shadow-sm transition-all"
            />
          </div>
          <p className="text-[11px] text-muted-foreground mt-1 pl-1">
            Updates timeline automatically.
          </p>
        </div>

        <div className="flex-1" />

        {/* Global Flex / Pinned Stats */}
        <div className="bg-sidebar-accent/50 rounded-xl p-4 border border-sidebar-border mb-4 shrink-0">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-semibold text-sidebar-foreground tracking-tight">Global FURI Benchmarks</h4>
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-xs text-muted-foreground">Active Patients</div>
              <div className="text-sm font-medium text-foreground">1,730 Nodes</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Conversion Rate</div>
              <div className="text-sm font-medium text-emerald-500">46.0% MCI-to-Dementia</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Hippocampal Atrophy</div>
              <div className="text-sm font-medium text-rose-500">3.9% Annual Loss</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
