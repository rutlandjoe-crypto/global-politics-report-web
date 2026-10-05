import type { MetadataRoute } from "next";
import fs from "fs";
import path from "path";
import {
  isClearlyWrongPoliticsSlug,
  normalizePoliticsStorySlug,
} from "@/lib/politicsUrlQuality";

const baseUrl = "https://www.globalpoliticsreport.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      changeFrequency: "hourly",
      priority: 1,
    },
  ];

  const editorialDir = path.join(process.cwd(), "app", "editorial");

  if (!fs.existsSync(editorialDir)) {
    return entries;
  }

  const directories = fs
    .readdirSync(editorialDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  const newestByStory = new Map<string, string>();

  for (const slug of directories) {
    if (isClearlyWrongPoliticsSlug(slug)) {
      continue;
    }

    const identity = normalizePoliticsStorySlug(slug);

    if (!identity) {
      continue;
    }

    const current = newestByStory.get(identity);

    if (!current || slug > current) {
      newestByStory.set(identity, slug);
    }
  }

  const uniqueSlugs =
    Array.from(newestByStory.values()).sort().reverse();

  for (const slug of uniqueSlugs) {
    entries.push({
      url: `${baseUrl}/editorial/${slug}`,
      changeFrequency: "monthly",
      priority: 0.7,
    });
  }

  return entries;
}
