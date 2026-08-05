import { readFile, stat, writeFile } from "node:fs/promises";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const directory = dirname(fileURLToPath(import.meta.url));
const sourceHtmlName = "OM_TEMP_검사운영위키_구성초안.html";
const reportDataName = "OM_TEMP_검사운영위키_보고용.js";
const wikiDataName = "OM_TEMP_검사운영위키_데이터.js";
const sentenceReviewName = "OM_TEMP_검사운영위키_문장검토.js";
const outputHtmlName = "OM_TEMP_operations_wiki_Claude_review_20260729.html";

const [sourceHtml, rawReportData, wikiData, sentenceReviewData] = await Promise.all([
  readFile(join(directory, sourceHtmlName), "utf8"),
  readFile(join(directory, reportDataName), "utf8"),
  readFile(join(directory, wikiDataName), "utf8"),
  readFile(join(directory, sentenceReviewName), "utf8"),
]);

const reviewRoutes = new Map([
  ["openmetadata-phase1-sharing-preview.html", "#topic-detail:branches"],
  ["openmetadata-phase2-verifier-table-preview.html", "#source-gates"],
  ["OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html", "#topic-detail:registration"],
  ["OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html", "#topic-detail:upgrade"],
  ["OM_TEMP_관리파일_필드_사전_미리보기.html", "#file-detail:manifest"],
  ["OM_TEMP_검사운영위키_구성초안.html", "#file-detail:manifest"],
  ["openmetadata-phase3-demo-preview.html", "#topic-detail:evidence"],
]);

const mimeType = (path) => {
  switch (extname(path).toLowerCase()) {
    case ".png":
      return "image/png";
    case ".json":
      return "application/json";
    case ".html":
      return "text/html;charset=utf-8";
    default:
      return "text/plain;charset=utf-8";
  }
};

const replaceEncodedAttribute = (source, attribute, value, replacement) =>
  source.replaceAll(
    `${attribute}=\\\"${value}\\\"`,
    `${attribute}=\\\"${replacement}\\\"`
  );

async function makeReportDataPortable(source) {
  let portable = source;
  const referencePattern = /(?:src|href)=\\\"([^\\\"]+)\\\"/g;
  const references = [...source.matchAll(referencePattern)].map((match) => match[1]);

  for (const reference of new Set(references)) {
    const route = reviewRoutes.get(reference.split("#")[0].split("/").at(-1));
    if (route) {
      portable = replaceEncodedAttribute(portable, "href", reference, route);
      continue;
    }
    if (
      reference.startsWith("http") ||
      reference.startsWith("data:") ||
      reference.startsWith("#")
    ) {
      continue;
    }
    const localPath = resolve(directory, reference);
    try {
      const metadata = await stat(localPath);
      if (!metadata.isFile()) continue;
      const content = await readFile(localPath);
      const dataUri = `data:${mimeType(localPath)};base64,${content.toString("base64")}`;
      portable = replaceEncodedAttribute(portable, "src", reference, dataUri);
      portable = replaceEncodedAttribute(portable, "href", reference, dataUri);
    } catch {
      // Non-file examples in code snippets remain plain text. Only actual
      // src/href files are required to make the review copy self-contained.
    }
  }
  return portable;
}

async function makeWikiDataPortable(source) {
  let portable = source;
  const evidencePattern = /\["((?:\.\.\/)+[^"]+)"\s*,/g;
  const references = [...source.matchAll(evidencePattern)].map((match) => match[1]);
  for (const reference of new Set(references)) {
    const localPath = resolve(directory, reference);
    try {
      const metadata = await stat(localPath);
      if (!metadata.isFile()) continue;
      const content = await readFile(localPath);
      const dataUri = `data:${mimeType(localPath)};base64,${content.toString("base64")}`;
      portable = portable.replaceAll(`["${reference}",`, `["${dataUri}",`);
    } catch {
      // A missing evidence file is preserved as a relative path so the
      // post-build dependency check can report it.
    }
  }
  const remainingReferences = [
    ...portable.matchAll(evidencePattern),
  ].map((match) => match[1]);
  if (remainingReferences.length > 0) {
    throw new Error(
      `Standalone wiki still has local evidence dependencies: ${remainingReferences.join(", ")}`
    );
  }
  return portable;
}

const reportData = await makeReportDataPortable(rawReportData);
const portableWikiData = await makeWikiDataPortable(wikiData);

const escapeClosingScript = (source) =>
  source.replace(/<\/script/gi, "<\\/script");

const embedScript = (sourceName, source) =>
  `<script data-embedded-source="${sourceName}">\n${escapeClosingScript(source)}\n</script>`;

const reportScriptTag = `<script src="${reportDataName}"></script>`;
const wikiScriptTag = `<script src="${wikiDataName}"></script>`;
const sentenceReviewScriptTag = `<script src="${sentenceReviewName}"></script>`;

if (
  !sourceHtml.includes(reportScriptTag) ||
  !sourceHtml.includes(wikiScriptTag) ||
  !sourceHtml.includes(sentenceReviewScriptTag)
) {
  throw new Error("Expected local data script tags were not found in the source HTML.");
}

const standaloneHtml = sourceHtml
  .replace(
    "<head>",
    "<head>\n  <!-- Claude review copy: local wiki data scripts and report assets are embedded below. -->"
  )
  .replace(
    "<title>OpenMetadata 커스터마이징 검사 운영 위키</title>",
    "<title>OpenMetadata 커스터마이징 검사 운영 위키 · Claude 검토용</title>"
  )
  .replace(reportScriptTag, embedScript(reportDataName, reportData))
  .replace(wikiScriptTag, embedScript(wikiDataName, portableWikiData))
  .replace(
    sentenceReviewScriptTag,
    embedScript(sentenceReviewName, sentenceReviewData),
  );

if (
  standaloneHtml.includes(reportScriptTag) ||
  standaloneHtml.includes(wikiScriptTag) ||
  standaloneHtml.includes(sentenceReviewScriptTag)
) {
  throw new Error("A local data script dependency remains in the standalone HTML.");
}

const unresolvedHtmlDependencies = [
  ...standaloneHtml.matchAll(
    /(?:src|href)=["']((?!https?:|data:|#|mailto:|\$\{)[^"'<>]+)["']/g
  ),
].map((match) => match[1]);
if (unresolvedHtmlDependencies.length > 0) {
  throw new Error(
    `Standalone HTML still has local dependencies: ${[
      ...new Set(unresolvedHtmlDependencies),
    ].join(", ")}`
  );
}

await writeFile(join(directory, outputHtmlName), standaloneHtml, "utf8");
console.log(join(directory, outputHtmlName));
