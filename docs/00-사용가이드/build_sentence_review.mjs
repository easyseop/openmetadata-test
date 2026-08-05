import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const docsDir = path.dirname(fileURLToPath(import.meta.url));
const dataPath = path.join(docsDir, "OM_TEMP_검사운영위키_데이터.js");
const htmlPath = path.join(docsDir, "OM_TEMP_검사운영위키_구성초안.html");
const baselinePath = path.join(
  docsDir,
  "OM_TEMP_검사운영위키_문장검토_원본_20260730.json",
);
const outputPath = path.join(
  docsDir,
  "OM_TEMP_검사운영위키_문장검토.js",
);

const excludedPathParts = new Set([
  "example",
  "resultExample",
  "failureExample",
  "command",
  "code",
  "before",
  "after",
  "evidence",
  "path",
]);

function loadWikiData() {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(dataPath, "utf8"), context);
  return context.window;
}

function extractObjectLiteral(source, declaration) {
  const marker = `const ${declaration} = `;
  const start = source.indexOf(marker);
  if (start < 0) throw new Error(`missing ${declaration}`);
  const objectStart = source.indexOf("{", start + marker.length);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let index = objectStart; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = null;
      continue;
    }
    if (character === '"' || character === "'" || character === "`") {
      quote = character;
      continue;
    }
    if (character === "{") depth += 1;
    if (character === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(objectStart, index + 1);
    }
  }
  throw new Error(`unterminated ${declaration}`);
}

function loadReportMap(html) {
  const literal = extractObjectLiteral(html, "REPORT_DETAIL_MAP");
  return vm.runInNewContext(`(${literal})`);
}

function isNarrative(value, location) {
  if (typeof value !== "string") return false;
  if (!/[가-힣]/.test(value) || value.includes("\n")) return false;
  if (value.trim().length < 12) return false;
  return !location.split(".").some((part) => excludedPathParts.has(part));
}

function collectObject(rows, chapter, page, value, location) {
  if (isNarrative(value, location)) {
    rows.push({
      id: `${chapter}|${page}|${location}`,
      chapter,
      page,
      location,
      text: value.trim(),
    });
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) =>
      collectObject(rows, chapter, page, item, `${location}.${index}`),
    );
    return;
  }
  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, item]) =>
      collectObject(rows, chapter, page, item, `${location}.${key}`),
    );
  }
}

function decodeText(value) {
  return value
    .replace(/<code[^>]*>([\s\S]*?)<\/code>/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/&middot;/g, "·")
    .replace(/&rarr;/g, "→")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function collectArticle(rows, chapter, page, html, articleId) {
  const pattern = new RegExp(
    `<article[^>]*id="${articleId}"[^>]*>([\\s\\S]*?)<\\/article>`,
  );
  const match = html.match(pattern);
  if (!match) return;
  const segments = match[1]
    .replace(
      /<\/(?:p|h1|h2|h3|li|td|th|section|div|span|strong)>/g,
      "$&\n",
    )
    .split("\n")
    .map(decodeText)
    .filter((text) => /[가-힣]/.test(text) && text.length >= 12);
  segments.forEach((text, index) => {
    rows.push({
      id: `${chapter}|${page}|article.${articleId}.${index}`,
      chapter,
      page,
      location: `article.${articleId}.${index}`,
      text,
    });
  });
}

function collectCurrent() {
  const wiki = loadWikiData();
  const html = fs.readFileSync(htmlPath, "utf8");
  const reportMap = loadReportMap(html);
  const rows = [];

  const topicPages = {
    "1": ["repositories", "branches", "identity"],
    "3": ["registration", "followup", "automation"],
    "4": ["upgrade", "conflicts"],
  };
  const filePages = {
    "3": [
      "manifest",
      "registry",
      "contracts",
      "shared_paths",
      "source_snapshot_owners",
      "diff_inventory",
      "layout",
      "zones",
    ],
    "4": ["candidate_lock", "test_run_set", "result", "patch_lock", "release_lock"],
  };

  Object.entries(topicPages).forEach(([chapter, keys]) => {
    keys.forEach((key) =>
      collectObject(
        rows,
        chapter,
        `상세 · ${wiki.WIKI_TOPICS[key].title}`,
        wiki.WIKI_TOPICS[key],
        `topic.${key}`,
      ),
    );
  });
  Object.entries(filePages).forEach(([chapter, keys]) => {
    keys.forEach((key) =>
      collectObject(
        rows,
        chapter,
        `상세 · ${wiki.WIKI_FILES[key].title}`,
        wiki.WIKI_FILES[key],
        `file.${key}`,
      ),
    );
  });
  Object.entries(wiki.WIKI_GATES).forEach(([key, gate]) =>
    collectObject(rows, "2", `상세 · ${gate.title}`, gate, `gate.${key}`),
  );

  const reportEntries = [
    ["1", "공유문서/openmetadata-phase1-sharing-preview.html"],
    ["2", "공유문서/openmetadata-phase2-verifier-table-preview.html"],
    ["3", "OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html"],
    ["4", "OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html"],
  ];
  reportEntries.forEach(([chapter, key]) => {
    collectObject(
      rows,
      chapter,
      "요약",
      reportMap[key],
      `report.${chapter}`,
    );
  });

  [
    ["2", "검사기 전체 목록", "gate-index"],
    ["2", "소스·등록 검사", "source-gates"],
    ["2", "업그레이드 영향 검사", "upgrade-gates"],
    ["2", "테스트·실행 검사", "runtime-gates"],
    ["2", "업그레이드·배포 검사", "release-gates"],
  ].forEach(([chapter, page, id]) =>
    collectArticle(rows, chapter, page, html, id),
  );

  return rows;
}

function reasonFor(action, original = "", final = "", location = "") {
  if (action === "유지") {
    if (
      /(?:\.title|\.group|Title)$/.test(location) ||
      (original.length < 45 &&
        !/(습니다|합니다|됩니다|않습니다|입니다|[.!?])$/.test(original))
    ) {
      return "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지";
    }
    if (
      /(?:\.fields|\.inputs|\.outputs|\.checks)\.\d+\.[01]$/.test(location) ||
      /(?:yaml|json|sha|paths|commit|branch|Manifest|Registry|Contract)/i.test(
        original,
      )
    ) {
      return "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시";
    }
    if (/예시|예:|경우|때/.test(original)) {
      return "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음";
    }
    if (/PASS|APPROVAL|BLOCK|ANALYSIS ERROR|NOT RUN/.test(original)) {
      return "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지";
    }
    return "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지";
  }
  if (action === "삭제") {
    return "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제";
  }
  if (action === "추가") {
    return "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가";
  }
  const termReasons = [
    [/정본/, "‘정본’ 대신 실제 기준 저장소를 직접 명시"],
    [/snapshot/, "snapshot을 ‘과거 전체 파일 복사본’으로 설명"],
    [/digest/, "digest를 ‘내용 확인값’으로 풀어 씀"],
    [/\bartifact\b/i, "artifact를 실제 이미지·패키지·배포 파일로 설명"],
    [/\bAST\b/, "AST가 하는 일을 ‘Python 함수 이름을 읽는 분석’으로 설명"],
    [/양방향|역방향/, "‘양방향·역방향’ 대신 서로 확인하는 두 항목을 직접 명시"],
    [/공식 계보/, "‘공식 계보’ 대신 ‘공식 버전에서 출발한 코드’로 설명"],
    [/원자 교체|rollback/, "구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"],
    [/leaf/, "leaf를 ‘마지막 JSON 항목’으로 설명"],
    [/파생/, "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"],
    [/\bref\b|worktree/, "Git 내부 용어 대신 branch·작업 폴더의 실제 상태를 설명"],
  ].filter(([pattern]) => pattern.test(original) && !pattern.test(final));
  if (termReasons.length > 0) {
    return termReasons.slice(0, 2).map(([, reason]) => reason).join(" · ");
  }
  if (original.length >= 120 && final.length < original.length) {
    return "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임";
  }
  if (/[·/]/.test(original) && final !== original) {
    return "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂";
  }
  return "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시";
}

function buildReview(baseline, current) {
  const stableId = (row) => `${row.chapter}|${row.location}`;
  const before = new Map(baseline.map((row) => [stableId(row), row]));
  const after = new Map(current.map((row) => [stableId(row), row]));
  const ids = [...new Set([...before.keys(), ...after.keys()])];
  return ids.map((id) => {
    const oldRow = before.get(id);
    const newRow = after.get(id);
    let action = "유지";
    if (!newRow) action = "삭제";
    else if (!oldRow) action = "추가";
    else if (oldRow.text !== newRow.text) action = "수정";
    return {
      id,
      chapter: newRow?.chapter ?? oldRow.chapter,
      page: newRow?.page ?? oldRow.page,
      location: newRow?.location ?? oldRow.location,
      original: oldRow?.text ?? "해당 문장 없음",
      action,
      final: newRow?.text ?? "삭제",
      reason: reasonFor(
        action,
        oldRow?.text,
        newRow?.text,
        newRow?.location ?? oldRow?.location,
      ),
    };
  });
}

const mode = process.argv[2];
const current = collectCurrent();
if (mode === "snapshot") {
  fs.writeFileSync(baselinePath, `${JSON.stringify(current, null, 2)}\n`);
  console.log(`${baselinePath}\n${current.length} narrative lines`);
} else if (mode === "build") {
  const baseline = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
  const review = buildReview(baseline, current);
  const counts = review.reduce(
    (result, row) => {
      result[row.action] = (result[row.action] ?? 0) + 1;
      return result;
    },
    {},
  );
  const payload = { generated_at: "2026-07-30", counts, rows: review };
  fs.writeFileSync(
    outputPath,
    `window.WIKI_SENTENCE_REVIEW = ${JSON.stringify(payload, null, 2)};\n`,
  );
  console.log(`${outputPath}\n${review.length} reviewed lines`);
  console.log(counts);
} else {
  throw new Error("usage: node build_sentence_review.mjs snapshot|build");
}
