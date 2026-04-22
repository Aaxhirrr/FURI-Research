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
    <aside className="fixed left-0 top-0 z-40 h-screen bg-black/40 backdrop-blur-xl border-r border-white/10 flex flex-col w-[300px] shadow-[4px_0_24px_rgba(0,0,0,0.5)]">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-3 w-full group cursor-pointer hover:scale-[1.02] transition-transform">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 bg-primary/20 shadow-[0_0_15px_rgba(120,119,198,0.5)]">
            <BrainCircuit className="w-5 h-5 text-primary group-hover:animate-pulse" />
          </div>
          <span className="font-extrabold text-xl bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 whitespace-nowrap">
            FURI Master
          </span>
        </div>
      </div>

      {/* Controls & Nav */}
      <div className="flex-1 p-4 space-y-6 overflow-y-auto flex flex-col">
        {/* Navigation Tabs */}
        <div className="space-y-1">
           <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider pl-3 mb-2 block">
              Application Modules
           </label>
           <button onClick={() => onTabChange('evaluate')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-300", activeTab === 'evaluate' ? "bg-white/10 text-white shadow-[inset_0_1px_rgba(255,255,255,0.1)]" : "text-gray-400 hover:bg-white/5 hover:text-white hover:translate-x-1")}>
              <LayoutDashboard className="w-4 h-4" /> Timeline Evaluation
           </button>
           <button onClick={() => onTabChange('graph')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-300", activeTab === 'graph' ? "bg-white/10 text-white shadow-[inset_0_1px_rgba(255,255,255,0.1)]" : "text-gray-400 hover:bg-white/5 hover:text-white hover:translate-x-1")}>
              <Network className="w-4 h-4" /> Global Knowledge Graph
           </button>
           <button onClick={() => onTabChange('consult')} className={cn("w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-300", activeTab === 'consult' ? "bg-white/10 text-white shadow-[inset_0_1px_rgba(255,255,255,0.1)]" : "text-gray-400 hover:bg-white/5 hover:text-white hover:translate-x-1")}>
              <MessageSquare className="w-4 h-4" /> Predictive Consultant
           </button>
        </div>

        {/* Patient Selector */}
        <div className="space-y-2 pt-4 border-t border-white/5">
          <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider pl-1">
            Active Patient ID
          </label>
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-white transition-colors" />
            <input
              type="text"
              value={rid}
              onChange={(e) => onRidSubmit(e.target.value)}
              placeholder="Search RID (e.g. 4022)"
              className="w-full bg-black/50 border border-white/10 rounded-lg pl-9 pr-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white placeholder:text-gray-600 shadow-inner transition-all hover:bg-black/70"
            />
          </div>
          <p className="text-[11px] text-gray-500 mt-1 pl-1">
            Updates timeline automatically.
          </p>
        </div>

        <div className="flex-1" />

        {/* Global Flex / Pinned Stats */}
        <div className="bg-gradient-to-br from-white/5 to-transparent backdrop-blur-md rounded-2xl p-4 border border-white/10 mb-4 shrink-0 shadow-[0_4px_30px_rgba(0,0,0,0.1)] group hover:border-white/20 transition-colors duration-500">
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-primary group-hover:drop-shadow-[0_0_8px_rgba(120,119,198,0.8)] transition-all" />
            <h4 className="text-sm font-semibold text-white tracking-tight">Global Benchmarks</h4>
          </div>
          <div className="space-y-3">
            <div className="group/stat cursor-default">
              <div className="text-[10px] uppercase font-bold text-gray-500 group-hover/stat:text-gray-400 transition-colors">Active Patients</div>
              <div className="text-sm font-medium text-gray-200">1,730 Nodes</div>
            </div>
            <div className="group/stat cursor-default">
              <div className="text-[10px] uppercase font-bold text-gray-500 group-hover/stat:text-gray-400 transition-colors">Conversion Rate</div>
              <div className="text-sm font-medium text-emerald-400/90 drop-shadow-[0_0_8px_rgba(52,211,153,0.3)]">46.0% MCI-to-Dementia</div>
            </div>
            <div className="group/stat cursor-default">
              <div className="text-[10px] uppercase font-bold text-gray-500 group-hover/stat:text-gray-400 transition-colors">Hippocampal Atrophy</div>
              <div className="text-sm font-medium text-rose-400/90 drop-shadow-[0_0_8px_rgba(251,113,133,0.3)]">3.9% Annual Loss</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
