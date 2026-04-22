"use client";

import { useState } from "react";
import { Sidebar } from "@/components/dashboard/sidebar";
import { OverviewSection } from "@/components/dashboard/sections/overview";
import { GraphSection } from "@/components/dashboard/sections/graph";
import { ConsultantSection } from "@/components/dashboard/sections/consultant";

export type Section = "evaluate" | "graph" | "consult";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Section>("evaluate");
  const [rid, setRid] = useState("4022"); // Default test subject

  const renderSection = () => {
    switch (activeTab) {
      case "evaluate":
        return <OverviewSection rid={rid} />;
      case "graph":
        return <GraphSection />;
      case "consult":
        return <ConsultantSection />;
      default:
        return <OverviewSection rid={rid} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-black bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] text-foreground font-sans selection:bg-primary/30">
      <div className="fixed inset-0 z-[-1] bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none mix-blend-overlay"></div>
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        rid={rid}
        onRidSubmit={(newRid: string) => setRid(newRid)}
      />
      <div className="flex-1 flex flex-col ml-[300px]">
        <main className="flex-1 p-8 overflow-auto">
          <div
            key={activeTab}
            className="animate-in fade-in zoom-in-95 slide-in-from-bottom-8 duration-700 ease-out fill-mode-both"
          >
            {renderSection()}
          </div>
        </main>
      </div>
    </div>
  );
}
