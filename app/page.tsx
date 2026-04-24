import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Global Politics Report",
  description: "Automated political journalism support for the modern newsroom.",
};

type JsonObject = { [key: string]: any };

function readLatestReport(): JsonObject {
  const filePath = path.join(process.cwd(), "public", "latest_report.json");

  try {
    if (!fs.existsSync(filePath)) {
      return {
        title: "GLOBAL POLITICS REPORT",
        generated_date: new Date().toLocaleString("en-US", {
          timeZone: "America/New_York",
        }),
        headline: "Latest report file not found.",
        snapshot: "Add public/latest_report.json to display live data.",
        key_storylines: [],
        sections: [],
      };
    }

    const raw = fs.readFileSync(filePath, "utf8");
    return JSON.parse(raw);
  } catch (e) {
    return {
      title: "GLOBAL POLITICS REPORT",
      generated_date: new Date().toLocaleString("en-US", {
        timeZone: "America/New_York",
      }),
      headline: "Error loading report.",
      snapshot: "Check JSON file.",
      key_storylines: [],
      sections: [],
    };
  }
}

function asArray(value: any): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v));
}

function SectionCard({ section }: { section: JsonObject }) {
  return (
    <div className="rounded-2xl border border-slate-300 bg-white p-4 shadow">
      <h3 className="mb-2 text-sm font-bold uppercase tracking-wide text-[#0f2747]">
        {section.title || "Coverage"}
      </h3>

      {section.headline && (
        <p className="mb-2 text-sm text-slate-800">{section.headline}</p>
      )}

      {section.snapshot && (
        <p className="mb-2 text-sm text-slate-600">{section.snapshot}</p>
      )}

      {section.key_storylines && (
        <ul className="space-y-1 text-sm text-slate-700">
          {asArray(section.key_storylines).map((item, i) => (
            <li key={i} className="ml-5 list-disc marker:text-red-600">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Page() {
  const data = readLatestReport();

  const sections = Array.isArray(data.sections) ? data.sections : [];

  return (
    <main className="min-h-screen bg-[#eef2f7] text-slate-950">
      <div className="mx-auto max-w-7xl px-4 py-6">

        {/* HEADER */}
        <header className="mb-6 rounded-3xl border border-slate-300 bg-white p-5 shadow-lg shadow-slate-300/40">
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">

            {/* LEFT HEADER */}
            <div>
              <div className="mb-4 inline-flex w-fit rounded-full border border-red-300 bg-red-50 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.28em] text-red-700">
                Politics Intelligence Desk
              </div>

              <h1 className="text-3xl font-black uppercase tracking-wide text-[#0f2747]">
                {data.title || "GLOBAL POLITICS REPORT"}
              </h1>

              <p className="mt-1 text-sm font-medium text-slate-600">
                Updated: {data.generated_date}
              </p>

              {data.headline && (
                <p className="mt-4 text-base font-semibold text-slate-900">
                  {data.headline}
                </p>
              )}

              {data.snapshot && (
                <p className="mt-2 text-sm text-slate-600">
                  {data.snapshot}
                </p>
              )}
            </div>

            {/* VIDEO */}
            <div className="overflow-hidden rounded-3xl border border-slate-300 bg-white shadow">
              <div className="border-b border-slate-300 bg-[#0f2747] px-4 py-3 text-xs font-bold uppercase tracking-widest text-white">
                Politics Live Video
              </div>

              <div className="aspect-video w-full bg-black">
                <iframe
                  className="h-full w-full"
                  src="https://www.youtube.com/embed/yY9dX2wQ6aQ?autoplay=1&mute=1"
                  title="Politics Live Stream"
                  allow="autoplay; encrypted-media; picture-in-picture"
                  allowFullScreen
                />
              </div>
            </div>

          </div>
        </header>

        {/* SECTIONS */}
        {sections.length > 0 && (
          <section className="grid gap-5 lg:grid-cols-2">
            {sections.map((section: JsonObject, i: number) => (
              <SectionCard key={i} section={section} />
            ))}
          </section>
        )}

        {/* FOOTER */}
        <footer className="mt-6 rounded-3xl border border-slate-300 bg-white p-5 text-center shadow">
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Global Politics Report
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Automated political journalism support for the modern newsroom.
          </p>
        </footer>

      </div>
    </main>
  );
}