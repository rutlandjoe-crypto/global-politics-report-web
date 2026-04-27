import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

type JsonObject = { [key: string]: any };

const VIDEO_URL = "https://www.youtube.com/embed/21X5lGlDOfg";

function readReport(): JsonObject {
  try {
    const filePath = path.join(process.cwd(), "public", "latest_report.json");
    const raw = fs.readFileSync(filePath, "utf8");
    return JSON.parse(raw);
  } catch {
    return {
      site: "Global Politics Report",
      brand: "Built for journalists, by a journalist.",
      headline: "Politics Report Loading",
      snapshot: "Latest political intelligence will appear here.",
      sections: [],
    };
  }
}

function asText(v: any): string {
  if (v === null || v === undefined) return "";
  return String(v).trim();
}

function asList(v: any): string[] {
  if (!v) return [];

  if (Array.isArray(v)) {
    return v
      .map((x) => {
        if (typeof x === "string") return x.trim();
        if (x && typeof x === "object") {
          return asText(x.text || x.title || x.headline || x.summary || x.name);
        }
        return asText(x);
      })
      .filter(Boolean);
  }

  if (typeof v === "string") {
    return v
      .split(/\n|•|- /)
      .map((x) => x.trim())
      .filter(Boolean);
  }

  return [];
}

function cleanTitle(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getSections(report: JsonObject): any[] {
  if (!report || typeof report !== "object") return [];

  if (Array.isArray(report.sections)) {
    return report.sections.filter(Boolean);
  }

  if (report.sections && typeof report.sections === "object") {
    return Object.entries(report.sections)
      .filter(([, value]) => value && typeof value === "object")
      .map(([key, value]: [string, any]) => ({
        id: value.id || key,
        title: value.title || cleanTitle(key),
        headline: value.headline || value.title || cleanTitle(key),
        snapshot: value.snapshot || value.summary || "",
        content: value.content || "",
        key_storylines:
          value.key_storylines ||
          value.keyStorylines ||
          value.storylines ||
          value.items ||
          [],
        updated_at: value.updated_at || value.generated_at || "",
      }));
  }

  return [];
}

function Card({ section }: { section: any }) {
  const title = asText(section.title || "Politics Report");
  const headline = asText(section.headline || title);
  const snapshot = asText(section.snapshot);
  const content = asText(section.content);
  const storylines = asList(section.key_storylines);

  const fallbackItems = content
    .split("\n")
    .map((line) => line.trim())
    .filter(
      (line) =>
        line.length > 25 &&
        !["HEADLINE", "SNAPSHOT", "KEY STORYLINES"].includes(line.toUpperCase())
    )
    .slice(0, 5);

  const items = storylines.length ? storylines : fallbackItems;

  return (
    <article className="rounded-3xl bg-white p-6 shadow-xl">
      <span className="text-xs font-black uppercase tracking-widest text-red-600">
        {title}
      </span>

      <h2 className="mt-3 text-2xl font-black text-slate-900">
        {headline}
      </h2>

      {snapshot ? (
        <p className="mt-4 text-base leading-7 text-slate-700">
          {snapshot}
        </p>
      ) : null}

      {items.length > 0 ? (
        <div className="mt-5 space-y-3">
          {items.map((item: string, i: number) => (
            <div
              key={i}
              className="border-l-4 border-red-600 bg-slate-50 px-4 py-3 text-sm font-semibold leading-6 text-slate-900"
            >
              {item}
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
}

export default function Home() {
  const report = readReport();

  const headline = asText(report.headline || "Global Politics Report");
  const snapshot = asText(
    report.snapshot ||
      "Real-time developments across government, elections, policy and power."
  );
  const updated = asText(report.updated_at || report.generated_at);

  const sections = getSections(report);
  const keyStorylines = asList(report.key_storylines);

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-7xl px-5 py-6">
        <header className="grid gap-8 border-b border-neutral-800 pb-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <span className="bg-red-700 px-4 py-2 text-xs font-black uppercase tracking-widest">
                GLOBAL POLITICS REPORT
              </span>

              <span className="border border-neutral-600 px-4 py-2 text-xs font-black uppercase tracking-widest">
                BUILT FOR JOURNALISTS
              </span>
            </div>

            <h1 className="text-5xl font-black leading-tight">
              {headline}
            </h1>

            <p className="mt-5 max-w-3xl text-lg text-neutral-300">
              {snapshot}
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              {updated ? (
                <span className="rounded-full bg-white px-4 py-2 text-xs font-bold text-black">
                  UPDATED {updated}
                </span>
              ) : null}

              <span className="rounded-full border border-red-500 px-4 py-2 text-xs font-bold text-red-300">
                {sections.length} REPORTS
              </span>
            </div>
          </div>

          <div className="rounded-3xl bg-neutral-900 p-5">
            <div className="mb-2 text-xs font-black uppercase text-red-400">
              LIVE POLITICS VIDEO
            </div>

            <div className="aspect-video overflow-hidden rounded-xl bg-black">
<iframe
  src={`${VIDEO_URL}?autoplay=1&mute=1`}
  title="Live Video"
  allow="autoplay; encrypted-media"
  allowFullScreen
  className="w-full h-full rounded-2xl"
/>
          </div>

            <div className="mt-3 text-xs text-neutral-400">
              Live politics video stream.
            </div>
          </div>
        </header>

        {keyStorylines.length > 0 ? (
          <section className="grid gap-4 py-6 md:grid-cols-2 lg:grid-cols-4">
            {keyStorylines.slice(0, 4).map((s, i) => (
              <div key={i} className="rounded-2xl border border-neutral-800 p-4">
                <p className="text-sm font-semibold">{s}</p>
              </div>
            ))}
          </section>
        ) : null}

        <section className="grid gap-6 py-8 lg:grid-cols-2">
          {sections.length ? (
            sections.map((s, i) => <Card key={s.id || i} section={s} />)
          ) : (
            <article className="rounded-3xl bg-white p-6 text-black">
              <h2 className="text-2xl font-black">No politics sections found.</h2>
              <p className="mt-3 font-semibold">
                Check public/latest_report.json and confirm the politics section exists.
              </p>
            </article>
          )}
        </section>

        <footer className="mt-10 text-center text-sm text-neutral-400">
          Global Politics Report · GSR Network
        </footer>
      </div>
    </main>
  );
}