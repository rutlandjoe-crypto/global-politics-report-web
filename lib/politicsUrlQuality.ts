/*
 * Global Politics Report sitemap quality controls.
 *
 * Conservative rules:
 * - normalize repeated dated source-headline URLs;
 * - reject unmistakable off-desk URLs;
 * - retain a URL whenever explicit political context exists.
 */

export function normalizePoliticsStorySlug(slug: string): string {
  return slug
    .toLowerCase()
    .replace(/^\d{4}-\d{2}-\d{2}-/, "")
    .replace(
      /-(cbsnews-com|nytimes-com|thehill-com|bbc-co-uk|aljazeera-com|cnn-com|reuters-com|apnews-com|npr-org|politico-com|axios-com|nbcnews-com|abcnews-go-com|foxnews-com)$/,
      ""
    )
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const explicitPolitics =
  /(trump|white-house|congress|senate|senator|representative|democrat|republican|gop|election|electoral|ballot|voter|campaign|governor|president|administration|cabinet|supreme-court|federal-court|justice-department|pentagon|state-department|legislation|government|minister|parliament|diplomat|sanction|tariff|zelensky|putin|netanyahu|iran-war|immigration|border|policy)/i;

const explicitForeignDesk =
  /(nfl|nba|mlb|nhl|wnba|ncaa|football|baseball|basketball|hockey|soccer|tennis|golf|nascar|formula-1|grand-prix|touchdown|quarterback|pitcher|home-run|playoff|semifinal|quarterfinal|djokovic|zverev|alcaraz|sinner|wimbledon|china-open|champions-league|premier-league|world-series|super-bowl|box-office|movie|actor|actress|singer|album|concert|netflix|celebrity|grammy|oscar|emmy|sportsbook|wager)/i;

export function isClearlyWrongPoliticsSlug(slug: string): boolean {
  const value = normalizePoliticsStorySlug(slug);

  if (explicitPolitics.test(value)) {
    return false;
  }

  return explicitForeignDesk.test(value);
}
