import assert from "node:assert/strict";
import { mergeEditorialStories } from "./archive-politics-editorial.mjs";

const prior = {
  headline: "Prior politics story",
  snapshot: "Prior context",
  url: "https://example.com/prior-politics-story",
  source_name: "Example",
  published: "2026-08-15T12:00:00Z",
};
const current = {
  headline: "Current politics story",
  snapshot: "Current context",
  url: "https://example.com/current-politics-story",
  source_name: "Example",
  published: "2026-08-16T12:00:00Z",
};

const merged = mergeEditorialStories(
  [prior],
  [{ live_newsroom: [current, prior, { headline: "Incomplete story" }] }],
);

assert.deepEqual(merged, [current, prior]);
assert.equal(
  merged.filter((story) => story.headline === "Prior politics story").length,
  1,
);
console.log("Politics editorial archive tests passed.");
