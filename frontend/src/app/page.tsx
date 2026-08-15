import Link from "next/link";
import { Eye, FileText, GitFork, Layers, Lock, Repeat, Server } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RUN_LABEL } from "@/lib/runs";
import "./landing.css";

const STEPS = [
  {
    n: "01",
    title: "Write the fork",
    body: "Name the product, set two prices, and choose when the change applies.",
    icon: GitFork,
    iconClass: "bg-emerald-50 text-emerald-600",
  },
  {
    n: "02",
    title: "Watch both worlds",
    body: "Buyers and the competitor decide in order. Nodes light as each agent speaks.",
    icon: Eye,
    iconClass: "bg-sky-50 text-sky-600",
  },
  {
    n: "03",
    title: "Read the paper",
    body: "Share, MRR, and the exact reasons that opened the gap — cited to the agent.",
    icon: FileText,
    iconClass: "bg-orange-50 text-orange-600",
  },
];

const METHOD = [
  { label: "4 rounds", icon: Repeat, iconClass: "bg-violet-50 text-violet-600" },
  { label: "Frozen roster", icon: Lock, iconClass: "bg-emerald-50 text-emerald-600" },
  { label: "One variable", icon: Layers, iconClass: "bg-sky-50 text-sky-600" },
  { label: "Local runtime", icon: Server, iconClass: "bg-orange-50 text-orange-600" },
];

export default function HomePage() {
  return (
    <main className="landing">
      <section className="mx-auto flex max-w-5xl flex-col items-center px-6 py-20 text-center md:py-28">
        <Badge variant="secondary" className="mb-4">
          Counterfactual replay
        </Badge>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight md:text-5xl">
          Change one thing. See who caused the rest.
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
          Run the same frozen market twice. Keep every variable locked except
          price. The gap between A and B is causal inside the sim — not a
          forecast.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Button asChild size="lg">
            <Link href="/new">Start a run</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/runs">Open workspace</Link>
          </Button>
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-4 px-6 md:grid-cols-[1.2fr_0.8fr]" aria-label="Product">
        <Card className="overflow-hidden border-0 bg-primary text-primary-foreground">
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Live orchestration</CardTitle>
            <Badge variant="outline" className="border-white/20 font-normal text-white/70">
              {RUN_LABEL.B} · round 3 / 4
            </Badge>
          </CardHeader>
          <CardContent>
            <svg viewBox="0 0 520 160" className="landing-console__chart" aria-hidden="true">
              <path
                d="M24 118 C 90 110, 150 96, 210 88 S 340 70, 496 64"
                fill="none"
                stroke="#c8c8d0"
                strokeWidth="2.5"
              />
              <path
                d="M24 118 C 90 112, 150 108, 210 92 S 340 48, 496 28"
                fill="none"
                stroke="#a1a1aa"
                strokeWidth="2.5"
              />
              <circle cx="210" cy="88" r="4" fill="#c8c8d0" />
              <circle cx="210" cy="92" r="4" fill="#a1a1aa" />
            </svg>
            <ul className="landing-console__agents">
              <li>
                <span>buyer_3</span>
                <em className="is-stay">{RUN_LABEL.A} stay</em>
                <em className="is-churn">{RUN_LABEL.B} churn</em>
              </li>
              <li>
                <span>competitor</span>
                <em className="is-stay">{RUN_LABEL.A} hold</em>
                <em className="is-match">{RUN_LABEL.B} match</em>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardDescription>The fork</CardDescription>
            <CardTitle className="text-2xl">$100 vs $120</CardTitle>
            <CardDescription>Same seed. Same roster. One price move.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between border-t pt-3">
              <span className="text-muted-foreground">{RUN_LABEL.A}</span>
              <span>Price stays put</span>
            </div>
            <div className="flex items-center justify-between border-t pt-3">
              <span className="text-muted-foreground">{RUN_LABEL.B}</span>
              <span>Only price changes</span>
            </div>
            <div className="flex items-center justify-between border-t pt-3">
              <span className="text-muted-foreground">Paper</span>
              <span>Who switched is the cause</span>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="mx-auto mt-16 grid max-w-5xl grid-cols-2 gap-4 px-6 md:grid-cols-4" aria-label="Method">
        {METHOD.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <CardHeader className="flex flex-row items-center gap-3 p-4">
                <div className={`flex size-9 shrink-0 items-center justify-center rounded-md ${item.iconClass}`}>
                  <Icon className="size-4" />
                </div>
                <CardTitle className="text-sm font-medium">{item.label}</CardTitle>
              </CardHeader>
            </Card>
          );
        })}
      </section>

      <section className="mx-auto grid max-w-5xl gap-4 px-6 py-16 md:grid-cols-3">
        {STEPS.map((step) => {
          const Icon = step.icon;
          return (
            <Card key={step.n}>
              <CardHeader>
                <div className={`mb-2 flex size-9 items-center justify-center rounded-md ${step.iconClass}`}>
                  <Icon className="size-4" />
                </div>
                <CardDescription>{step.n}</CardDescription>
                <CardTitle>{step.title}</CardTitle>
                <CardDescription className="text-sm leading-relaxed">{step.body}</CardDescription>
              </CardHeader>
            </Card>
          );
        })}
      </section>

      <section className="border-t bg-secondary">
        <div className="mx-auto max-w-5xl px-6 py-16">
          <p className="text-sm font-medium text-muted-foreground">How a run works</p>
          <h2 className="mt-2 max-w-xl text-3xl font-semibold tracking-tight">
            Current world. Changed world. Same seed.
          </h2>
          <div className="mt-8 grid gap-6 md:grid-cols-3">
            <div>
              <p className="font-medium">{RUN_LABEL.A}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Price stays put. The roster plays the market as written.
              </p>
            </div>
            <div>
              <p className="font-medium">{RUN_LABEL.B}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Only the price changes. Everything else is frozen.
              </p>
            </div>
            <div>
              <p className="font-medium">The paper</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Whoever switched, churned, or matched is the cause of the rest.
              </p>
            </div>
          </div>
          <Button asChild className="mt-8" size="lg">
            <Link href="/new">New experiment</Link>
          </Button>
        </div>
      </section>
    </main>
  );
}
