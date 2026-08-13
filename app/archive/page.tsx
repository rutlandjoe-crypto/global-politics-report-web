import type { Metadata } from "next";
import Link from "next/link";
import { getEditorialItems, SITE_URL } from "../lib/editorial-archive";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Editorial Archive | Global Politics Report",
  description: "Permanent Global Politics Report editorial coverage and source links.",
  alternates: { canonical: `${SITE_URL}/archive` },
};

export default async function ArchivePage() {
  const items = await getEditorialItems();

  return (
    <main className="bg-slate-100 px-5 py-10 text-slate-950">
      <section className="mx-auto max-w-4xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-10">
        <h1 className="text-3xl font-black">Global Politics Report Editorial Archive</h1>
        <ul className="mt-6 space-y-5">
          {items.map((item) => (
            <li key={item.slug} className="border-b border-slate-200 pb-5">
              <Link className="font-bold text-blue-900 hover:underline" href={`/editorial/${item.slug}`}>
                {item.headline}
              </Link>
              <time className="mt-2 block text-sm text-slate-600" dateTime={new Date(item.published).toISOString()}>
                {item.published}
              </time>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
