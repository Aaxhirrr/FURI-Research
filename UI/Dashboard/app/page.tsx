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
    <div className="flex min-h-screen bg-background text-foreground font-sans">
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
            className="animate-in fade-in slide-in-from-bottom-4 duration-500"
          >
            {renderSection()}
          </div>
        </main>
      </div>
    </div>
  );
}
