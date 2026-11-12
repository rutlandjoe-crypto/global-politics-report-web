import type { MetadataRoute } from "next";
import { getEditorialItems, SITE_URL } from "./lib/editorial-archive";

export const dynamic = "force-dynamic";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const items = await getEditorialItems();

  return [
    { url: `${SITE_URL}/` },
    { url: `${SITE_URL}/archive` },
    ...items.slice(0, 49_998).map(({ slug }) => ({
      url: `${SITE_URL}/editorial/${slug}`,
    })),
  ];
}
