import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

type JsonObject = { [key: string]: any };

// ✅ VIDEO FALLBACK CHAIN
const DEFAULT_VIDEO =
  process.env.NEXT_PUBLIC_GPR_VIDEO_URL ||
  "https://www.youtube.com/embed/21X5lGlDOfg?rel=0&autoplay=1&mute=1";

function readReport(): JsonObject {
  try {
    const filePath = path.join(process.cwd(), "public", "latest_report.json");
    const raw = fs.readFileSync(filePath, "utf8");
    return JSON.parse(raw);
  } catch {
    return {
      headline: "Politics Report Loading",
      snapshot: "",
      sections: [],
    };
  }
}

function clean(v: any): string {
  if (!v) return "";
  return String(v).replace(/\s+/g, " ").trim();
}

function normalizeVideoUrl(value: any): string {
  const url = clean(value) || DEFAULT_VIDEO;

  const needsRel = !url.includes("rel=");
  const needsAutoplay = !url.includes("autoplay=");
  const needsMute = !url.includes("mute=");

  const params = [
    needsRel ? "rel=0" : "",
    needsAutoplay ? "autoplay=1" : "",
    needsMute ? "mute=1" : "",
  ].filter(Boolean);

  if (!params.length) return url;

  return `${url}${url.includes("?") ? "&" : "?"}${params.join("&")}`;
}

function list(v: any): string[] {
  if (!v) return [];

  if (Array.isArray(v)) return v.map(clean).filter(Boolean);

  if (typeof v === "string") {
    return v
      .split(/\n|•|- /)
      .map((x) => x.trim())
      .filter(Boolean);
  }

  return [];
}

function getStories(report: JsonObject): any[] {
  if (Array.isArray(report.sections)) return report.sections;

  if (report.sections && typeof report.sections === "object") {
    return Object.values(report.sections);
  }

  return [];
}

// 🔥 STORY CARD (REAL STRUCTURE)
function StoryCard({ story, index }: { story: any; index: number }) {
  const headline = clean(story.headline) || `Politics Story ${index + 1}`;
  const url = clean(story.url) || "#";
  const summary = clean(story.snapshot || story.summary);

  const keyData = list(story.key_data);
  const why = list(story.why_it_matters);
  const watch = list(story.what_to_watch);

  return (
    <div className="mb-6 rounded-xl border border-neutral-800 bg-neutral-900 p-5">
      {/* HEADLINE */}
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-2xl font-extrabold text-white hover:text-red-400"
      >
        {headline}
      </a>

      {/* SUMMARY */}
      {summary && <div className="mt-2 text-sm text-neutral-400">{summary}</div>}

      {/* DATA GRID */}
      <div className="mt-4 grid gap-4 md:grid-cols-3">
        {/* KEY DATA */}
        <div className="rounded-lg bg-black p-3">
          <div className="mb-2 text-xs font-black text-red-400">KEY DATA</div>
          {keyData.length ? (
            keyData.map((d, i) => (
              <div key={i} className="border-b border-neutral-800 py-1 text-sm">
                {d}
              </div>
            ))
          ) : (
            <div className="text-sm text-neutral-500">No data</div>
          )}
        </div>

        {/* WHY IT MATTERS */}
        <div className="rounded-lg bg-black p-3">
          <div className="mb-2 text-xs font-black text-red-400">WHY IT MATTERS</div>
          {why.length ? (
            why.map((d, i) => (
              <div key={i} className="border-b border-neutral-800 py-1 text-sm">
                {d}
              </div>
            ))
          ) : (
            <div className="text-sm text-neutral-500">Editorial impact developing</div>
          )}
        </div>

        {/* WHAT TO WATCH */}
        <div className="rounded-lg bg-black p-3">
          <div className="mb-2 text-xs font-black text-red-400">WHAT TO WATCH</div>
          {watch.length ? (
            watch.map((d, i) => (
              <div key={i} className="border-b border-neutral-800 py-1 text-sm">
                {d}
              </div>
            ))
          ) : (
            <div className="text-sm text-neutral-500">Next movement pending</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const report = readReport();

  const headline = clean(report.headline) || "Politics Report Loading";
  const snapshot = clean(report.snapshot);
  const updated = clean(report.updated_at || report.generated_at);
  const videoUrl = normalizeVideoUrl(report.video_url);

  let stories = getStories(report);

  if (!stories.length) {
    stories = [
      {
        headline,
        snapshot,
        key_data: ["Politics pipeline awaiting update"],
        why_it_matters: ["Coverage gap for newsroom"],
        what_to_watch: ["Next content engine run"],
      },
    ];
  }

  const keyStorylines = list(report.key_storylines);

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-4 py-6">
        {/* HEADER */}
        <header className="mb-6 border-b border-neutral-800 pb-6">
          <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
            <div>
              <div className="mb-2 text-xs font-black uppercase tracking-widest text-red-400">
                GLOBAL POLITICS REPORT
              </div>

              <h1 className="text-4xl font-extrabold">{headline}</h1>

              {snapshot && <p className="mt-3 max-w-2xl text-neutral-400">{snapshot}</p>}

              <div className="mt-3 text-xs text-neutral-500">Updated {updated}</div>
            </div>

            {/* VIDEO */}
            <div>
              <div className="mb-2 text-xs font-bold text-red-400">LIVE COVERAGE</div>

              <div className="aspect-video overflow-hidden rounded-xl border border-neutral-800 bg-black">
                <iframe
                  src={videoUrl}
                  title="Live Politics Coverage"
                  allow="autoplay; encrypted-media; picture-in-picture"
                  allowFullScreen
                  className="h-full w-full"
                />
              </div>

              <div className="mt-2 text-xs text-neutral-500">Live politics news stream</div>
            </div>
          </div>
        </header>

        {/* STORYLINES */}
        <section className="mb-6">
          {keyStorylines.map((s, i) => (
            <div key={i} className="border-b border-neutral-800 py-2">
              {s}
            </div>
          ))}
        </section>

        {/* STORIES */}
        <section>
          {stories.slice(0, 10).map((s, i) => (
            <StoryCard key={i} story={s} index={i} />
          ))}
        </section>

        {/* TOOLKIT */}
        <section className="mt-8 border-t border-neutral-800 pt-6">
          <div className="mb-3 text-xs font-black uppercase text-red-400">
            Journalist Toolkit
          </div>

          <div className="space-y-2 text-sm">
            <a
              href="https://www.reuters.com/world/politics/"
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:underline"
            >
              Reuters Politics
            </a>
            <a
              href="https://apnews.com/hub/politics"
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:underline"
            >
              Associated Press
            </a>
            <a
              href="https://www.politico.com"
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:underline"
            >
              Politico
            </a>
            <a
              href="https://rollcall.com"
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:underline"
            >
              Roll Call
            </a>
            <a
              href="https://thehill.com"
              target="_blank"
              rel="noopener noreferrer"
              className="block hover:underline"
            >
              The Hill
            </a>
          </div>
        </section>
      </div>
    </main>
  );
}