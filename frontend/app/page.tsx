"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ShieldCheck,
  GitBranch,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Send,
  RefreshCw,
  Gavel,
  ListChecks,
} from "lucide-react";
import { api, CompletionResponse, LedgerEntry } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useToast } from "@/components/ui/use-toast";

const STATUS_STYLES: Record<string, string> = {
  allowed: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  warned: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  needs_review: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  rejected: "bg-rose-500/15 text-rose-300 border-rose-500/30",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status] || ""}`}
    >
      {status}
    </span>
  );
}

function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-panel/60 backdrop-blur p-5 shadow-xl ${className}`}
    >
      {children}
    </div>
  );
}

export default function Dashboard() {
  const [prompt, setPrompt] = useState(
    "What credit score is considered high risk for underwriting?",
  );
  const [risk, setRisk] = useState("low");
  const [domain, setDomain] = useState("underwriting");
  const [useRag, setUseRag] = useState(true);
  const [loading, setLoading] = useState(false);
  const [resp, setResp] = useState<CompletionResponse | null>(null);
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [queue, setQueue] = useState<LedgerEntry[]>([]);
  const [verify, setVerify] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const refresh = useCallback(async () => {
    try {
      const [l, q, v] = await Promise.all([
        api.ledger(),
        api.reviewQueue(),
        api.verify(),
      ]);
      setLedger(l);
      setQueue(q);
      setVerify(v);
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const submit = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await api.complete({
        prompt,
        risk_level: risk,
        domain: domain || undefined,
        use_rag: useRag,
      });
      setResp(r);
      toast({
        title: `Decision: ${r.status}`,
        description: `${r.provider} · faithfulness ${r.evaluation.faithfulness}`,
        tone:
          r.status === "allowed"
            ? "success"
            : r.status === "rejected"
              ? "error"
              : "warning",
      });
      await refresh();
    } catch (e: any) {
      setError(e.message);
      toast({ title: "Request failed", description: e.message, tone: "error" });
    } finally {
      setLoading(false);
    }
  };

  const decide = async (id: string, decision: string, note?: string) => {
    try {
      await api.review(id, { decision, reviewer: "console-user", note });
      toast({
        title: `Review: ${decision}`,
        description: "Recorded immutably in the audit ledger.",
        tone: decision === "approve" ? "success" : "error",
      });
      await refresh();
    } catch (e: any) {
      setError(e.message);
      toast({ title: "Review failed", description: e.message, tone: "error" });
    }
  };

  const kpis = useMemo(() => {
    const total = ledger.length;
    const cost = ledger.reduce((s, e) => s + e.cost_usd, 0);
    const avgLat = total
      ? ledger.reduce((s, e) => s + e.latency_ms, 0) / total
      : 0;
    const counts: Record<string, number> = {};
    ledger.forEach((e) => (counts[e.status] = (counts[e.status] || 0) + 1));
    return { total, cost, avgLat, counts };
  }, [ledger]);

  return (
    <TooltipProvider delayDuration={150}>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-accent">
              <ShieldCheck className="h-7 w-7" />
              <h1 className="text-2xl font-bold text-white">VerityGate</h1>
            </div>
            <p className="mt-1 text-sm text-slate-400">
              Route models. Verify evidence. Govern decisions.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {verify && (
              <span
                className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm ${
                  verify.valid
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                    : "border-rose-500/30 bg-rose-500/10 text-rose-300"
                }`}
              >
                <GitBranch className="h-4 w-4" />
                ledger{" "}
                {verify.valid ? "verified" : `tampered: ${verify.reason}`}
              </span>
            )}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={refresh}
                  aria-label="Refresh"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Refresh ledger &amp; queue</TooltipContent>
            </Tooltip>
          </div>
        </header>

        {error && (
          <div className="mb-4 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-300">
            {error} — is the backend running on :8009?
          </div>
        )}

        {/* KPIs */}
        <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          <Kpi
            icon={<Activity className="h-5 w-5" />}
            label="Decisions"
            value={kpis.total.toString()}
          />
          <Kpi
            icon={<Clock className="h-5 w-5" />}
            label="Avg latency"
            value={`${kpis.avgLat.toFixed(0)} ms`}
          />
          <Kpi
            icon={<CheckCircle2 className="h-5 w-5" />}
            label="Cost (USD)"
            value={`$${kpis.cost.toFixed(4)}`}
          />
          <Kpi
            icon={<AlertTriangle className="h-5 w-5" />}
            label="In review"
            value={queue.length.toString()}
          />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Playground */}
          <Card className="lg:col-span-1">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-400">
              Completion Playground
            </h2>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              className="w-full resize-none rounded-lg border border-white/10 bg-ink/60 p-3 text-sm outline-none focus:border-accent"
            />
            <div className="mt-3 grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="risk">Risk level</Label>
                <Select value={risk} onValueChange={setRisk}>
                  <SelectTrigger id="risk">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">low</SelectItem>
                    <SelectItem value="medium">medium</SelectItem>
                    <SelectItem value="high">high</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label htmlFor="domain">Domain</Label>
                <input
                  id="domain"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  className="h-9 w-full rounded-lg border border-white/10 bg-ink/60 px-3 text-sm text-slate-200 outline-none focus:border-accent"
                />
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2">
              <Checkbox
                id="rag"
                checked={useRag}
                onCheckedChange={(v) => setUseRag(v === true)}
              />
              <Label htmlFor="rag" className="cursor-pointer">
                Use RAG retrieval (evidence + citations)
              </Label>
            </div>
            <Button onClick={submit} disabled={loading} className="mt-4 w-full">
              <Send className="h-4 w-4" />
              {loading ? "Governing..." : "Run governed completion"}
            </Button>

            {resp && (
              <div className="mt-5 space-y-3 pt-1">
                <Separator />
                <div className="flex items-center justify-between">
                  <StatusBadge status={resp.status} />
                  <span className="text-xs text-slate-500">
                    {resp.provider} · {resp.latency_ms.toFixed(0)}ms{" "}
                    {resp.cached && "· cached"}
                  </span>
                </div>
                <p className="rounded-lg bg-ink/60 p-3 text-sm text-slate-300">
                  {resp.output}
                </p>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <Meter label="faithful" v={resp.evaluation.faithfulness} />
                  <Meter
                    label="coverage"
                    v={resp.evaluation.citation_coverage}
                  />
                  <Meter label="policy" v={resp.evaluation.policy_score} />
                </div>
                <div className="flex flex-wrap items-center gap-2 text-[10px]">
                  <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-slate-400">
                    policy:{" "}
                    <span className="text-accent">
                      {resp.evaluation.policy}
                    </span>
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-slate-400">
                    judge:{" "}
                    <span className="text-accent">{resp.evaluation.judge}</span>
                  </span>
                </div>
                {resp.evaluation.rationale && (
                  <p className="rounded-lg border border-white/10 bg-ink/60 px-3 py-2 text-xs italic text-slate-400">
                    “{resp.evaluation.rationale}”
                  </p>
                )}
                {resp.evaluation.failed_checks.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {resp.evaluation.failed_checks.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-rose-500/15 px-2 py-0.5 text-[10px] font-medium text-rose-300"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                )}
                {resp.citations.length > 0 && (
                  <div className="space-y-1">
                    {resp.citations.map((c) => (
                      <div
                        key={c.doc_id}
                        className="rounded bg-white/5 px-2 py-1 text-xs text-slate-400"
                      >
                        <span className="text-accent">[{c.doc_id}]</span>{" "}
                        {c.snippet.slice(0, 90)}…
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </Card>

          {/* Governance: tabs */}
          <Card className="lg:col-span-2">
            <Tabs defaultValue="queue">
              <TabsList>
                <TabsTrigger value="queue">
                  <Gavel className="h-3.5 w-3.5" /> Review Queue ({queue.length}
                  )
                </TabsTrigger>
                <TabsTrigger value="ledger">
                  <ListChecks className="h-3.5 w-3.5" /> Decision Ledger (
                  {ledger.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="queue">
                <p className="mb-3 text-xs text-slate-500">
                  The deterministic gate withheld these for a human. The model
                  cannot self-approve a high-risk decision.
                </p>
                {queue.length === 0 ? (
                  <p className="py-8 text-center text-sm text-slate-500">
                    No decisions awaiting review.
                  </p>
                ) : (
                  <ScrollArea className="max-h-[440px]">
                    <div className="space-y-3 pr-3">
                      {queue.map((e) => (
                        <div
                          key={e.decision_id}
                          className="rounded-lg border border-white/10 bg-ink/40 p-3"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <StatusBadge status={e.status} />
                              <span className="text-xs text-slate-500">
                                risk: {e.risk_level}
                              </span>
                            </div>
                            <span className="font-mono text-[10px] text-slate-600">
                              {e.decision_id.slice(0, 12)}
                            </span>
                          </div>
                          <p className="mt-2 text-xs text-slate-400">
                            failed: faithfulness {e.faithfulness}, coverage{" "}
                            {e.citation_coverage}
                          </p>
                          <div className="mt-3">
                            <ReviewDialog entry={e} onDecide={decide} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </TabsContent>

              <TabsContent value="ledger">
                <ScrollArea className="max-h-[480px]">
                  <Accordion type="single" collapsible className="w-full">
                    {ledger.map((e) => (
                      <AccordionItem key={e.decision_id} value={e.decision_id}>
                        <AccordionTrigger className="px-1">
                          <div className="flex flex-1 items-center gap-3">
                            <StatusBadge status={e.status} />
                            <span className="text-slate-400">{e.provider}</span>
                            <span className="text-slate-500">
                              risk: {e.risk_level}
                            </span>
                            <span className="ml-auto mr-2 font-mono text-[10px] text-slate-600">
                              {e.decision_hash.slice(0, 16)}…
                            </span>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="px-1">
                          <div className="grid grid-cols-3 gap-2">
                            <Detail
                              label="faithfulness"
                              value={String(e.faithfulness)}
                            />
                            <Detail
                              label="citation coverage"
                              value={String(e.citation_coverage)}
                            />
                            <Detail
                              label="policy score"
                              value={String(e.policy_score)}
                            />
                            <Detail
                              label="cost"
                              value={`$${e.cost_usd.toFixed(4)}`}
                            />
                            <Detail
                              label="latency"
                              value={`${e.latency_ms.toFixed(0)} ms`}
                            />
                            <Detail label="gate status" value={e.gate_status} />
                          </div>
                          <div className="mt-3 space-y-1">
                            <HashRow label="input" value={e.input_hash} />
                            <HashRow label="evidence" value={e.evidence_hash} />
                            <HashRow label="output" value={e.output_hash} />
                            <HashRow label="decision" value={e.decision_hash} />
                            <HashRow
                              label="prev"
                              value={e.prev_hash || "GENESIS"}
                            />
                          </div>
                          {e.reviewer && (
                            <p className="mt-3 text-xs text-slate-400">
                              Reviewed by{" "}
                              <span className="text-accent">{e.reviewer}</span>
                              {e.review_decision
                                ? ` · ${e.review_decision}`
                                : ""}
                              {e.review_note ? ` · ${e.review_note}` : ""}
                            </p>
                          )}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </Card>
        </div>

        <footer className="mt-10 flex flex-col items-center gap-1 border-t border-white/10 pt-6 text-center text-xs text-slate-500">
          <p>Route models. Verify evidence. Govern decisions.</p>
          <p>
            Built &amp; designed by{" "}
            <a
              href="https://github.com/deciwa"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-slate-400 hover:text-accent"
            >
              Deciwa
            </a>
          </p>
        </footer>
      </main>
    </TooltipProvider>
  );
}

function ReviewDialog({
  entry,
  onDecide,
}: {
  entry: LedgerEntry;
  onDecide: (id: string, decision: string, note?: string) => void;
}) {
  const [note, setNote] = useState("");
  const [open, setOpen] = useState(false);
  const act = (decision: string) => {
    onDecide(entry.decision_id, decision, note || undefined);
    setOpen(false);
    setNote("");
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Gavel className="h-3.5 w-3.5" /> Review
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Human review</DialogTitle>
          <DialogDescription>
            Decision{" "}
            <span className="font-mono text-slate-300">
              {entry.decision_id.slice(0, 12)}
            </span>{" "}
            · risk {entry.risk_level}. Your decision is recorded immutably in
            the audit ledger.
          </DialogDescription>
        </DialogHeader>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={3}
          placeholder="Reviewer note (optional)"
          className="w-full resize-none rounded-lg border border-white/10 bg-ink/60 p-3 text-sm outline-none focus:border-accent"
        />
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="reject" size="sm" onClick={() => act("reject")}>
            <XCircle className="h-3.5 w-3.5" /> Reject
          </Button>
          <Button variant="approve" size="sm" onClick={() => act("approve")}>
            <CheckCircle2 className="h-3.5 w-3.5" /> Approve
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Kpi({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <Card>
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-accent/15 p-2 text-accent">{icon}</div>
        <div>
          <p className="text-xs text-slate-400">{label}</p>
          <p className="text-xl font-semibold text-white">{value}</p>
        </div>
      </div>
    </Card>
  );
}

function Meter({ label, v }: { label: string; v: number }) {
  const pct = Math.round(v * 100);
  const color =
    v >= 0.7 ? "bg-emerald-400" : v >= 0.5 ? "bg-amber-400" : "bg-rose-400";
  return (
    <div className="rounded-lg bg-ink/60 p-2">
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-1 text-[10px] text-slate-400">
        {label} {pct}%
      </p>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-ink/60 p-2">
      <p className="text-[10px] uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="text-slate-300">{value}</p>
    </div>
  );
}

function HashRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 font-mono text-[10px] text-slate-500">
      <span className="w-16 shrink-0 text-slate-600">{label}</span>
      <span className="truncate">{value}</span>
    </div>
  );
}
