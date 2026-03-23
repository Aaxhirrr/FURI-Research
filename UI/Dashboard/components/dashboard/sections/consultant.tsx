"use client";
import React, { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, AlertCircle, Network } from "lucide-react";

export function ConsultantSection() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    const userMsg = { role: "user", content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const res = await fetch("/api/consult", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content })
      });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || "Consultant request failed");

      setMessages(prev => [...prev, { role: "assistant", data }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: "error", content: err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-5xl mx-auto animate-in fade-in duration-500">
      <div className="mb-6 shrink-0">
        <h2 className="text-2xl font-bold tracking-tight">Predictive Consultant AI</h2>
        <p className="text-muted-foreground">MultiClin NER extraction bridging EN, ES, IT, NL, RO, SV, CS to the Graph.</p>
      </div>

      <div className="flex-1 bg-card border border-border rounded-xl shadow-sm flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground space-y-4">
              <Bot className="w-12 h-12 text-primary/40" />
              <p>Type a clinical query in supported languages to begin finding predictive twin paths.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
             <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
               {msg.role !== 'user' && (
                 <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                   {msg.role === 'error' ? <AlertCircle className="w-4 h-4 text-destructive" /> : <Bot className="w-4 h-4 text-primary" />}
                 </div>
               )}
               <div className={`max-w-[80%] rounded-xl p-4 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted border border-border shadow-sm'}`}>
                 {msg.role === 'user' || msg.role === 'error' ? (
                   <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                 ) : (
                   <div className="space-y-4 text-sm leading-relaxed text-foreground">
                     {msg.data.entities && msg.data.entities.length > 0 && (
                       <div className="bg-background/50 rounded-lg p-3 border border-border/50">
                         <h4 className="font-semibold text-xs uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2"><Network className="w-3 h-3 text-primary" /> Entities Extracted & Projected</h4>
                         {msg.data.entities.map((e: any, i: number) => (
                           <div key={i} className="text-xs mb-1">
                             <span className="font-mono text-primary">{e.original}</span> <span className="text-muted-foreground">({e.type})</span> ➔ <span className="font-semibold tracking-wide">{e.projected_node}</span>
                           </div>
                         ))}
                       </div>
                     )}
                     {msg.data.evidence && msg.data.evidence.length > 0 && (
                       <div className="bg-emerald-500/10 rounded-lg p-3 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-mono text-xs whitespace-pre-wrap leading-loose">
                         {msg.data.evidence.join("\n")}
                       </div>
                     )}
                     <div className="whitespace-pre-wrap border-t border-border pt-3 mt-3">{msg.data.assessment}</div>
                   </div>
                 )}
               </div>
               {msg.role === 'user' && (
                 <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                   <User className="w-4 h-4 text-secondary-foreground" />
                 </div>
               )}
             </div>
          ))}
          {loading && (
            <div className="flex gap-4">
               <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0 hidden sm:flex">
                 <Bot className="w-4 h-4 text-primary animate-pulse" />
               </div>
               <div className="bg-muted border border-border rounded-xl p-4 flex items-center gap-3">
                 <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                 <span className="text-sm text-muted-foreground">Extracting, Projecting, and Querying Graph...</span>
               </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-muted/20">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Paciente de 72 años con pérdida de memoria severa..."
              className="flex-1 bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm transition-all"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()} className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center shadow-sm">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
