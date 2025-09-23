import Link from "next/link";
import { Header } from "../components/Header";

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col gap-10">
      <Header />
      <section className="grid gap-6 md:grid-cols-2">
        <FeatureCard
          title="Build Offense Lineup"
          description="Select 11 offensive players, compute LSU/LIU/LIC and visualize relationship strength in seconds."
          href="/builder?side=offense"
        />
        <FeatureCard
          title="Build Defense Lineup"
          description="Track defensive continuity by coordinator window, coverage shell and positional chemistry."
          href="/builder?side=defense"
        />
      </section>
      <section className="card space-y-4">
        <h2 className="text-lg font-semibold">How it works</h2>
        <ol className="space-y-3 text-sm text-slate-600">
          <li><strong>Pick the window.</strong> Choose the team, side and play-caller system state to anchor your evaluation.</li>
          <li><strong>Select 11 players.</strong> Snap counts, position groups and IUS metrics guide who truly understands their job.</li>
          <li><strong>Review chemistry.</strong> Weighted Jaccard edges reveal which pairs have actually played together.</li>
        </ol>
      </section>
    </main>
  );
}

interface FeatureCardProps {
  title: string;
  description: string;
  href: string;
}

function FeatureCard({ title, description, href }: FeatureCardProps) {
  return (
    <Link href={href} className="card group transition hover:-translate-y-1 hover:shadow-lg">
      <h3 className="text-xl font-semibold group-hover:text-primary">{title}</h3>
      <p className="mt-2 text-sm text-slate-500">{description}</p>
      <span className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-primary">
        Launch builder →
      </span>
    </Link>
  );
}

