#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { minify } = require("html-minifier-terser");
const CleanCSS = require("clean-css");
const terser = require("terser");
const JavaScriptObfuscator = require("javascript-obfuscator");

function collectFiles(rootDir) {
  const files = [];
  const stack = [rootDir];

  while (stack.length > 0) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(fullPath);
      } else if (entry.isFile()) {
        files.push(fullPath);
      }
    }
  }

  files.sort();
  return files;
}

function minifyCss(source) {
  const result = new CleanCSS({
    level: {
      1: {
        all: true,
      },
      2: {
        all: false,
      },
    },
  }).minify(source);

  if (result.errors && result.errors.length > 0) {
    throw new Error(`CSS minification failed: ${result.errors.join("; ")}`);
  }

  return result.styles || source;
}

async function minifyInlineJs(code, moduleMode = false) {
  const result = await terser.minify(code, {
    module: moduleMode,
    compress: {
      passes: 2,
      drop_console: false,
    },
    mangle: false,
    format: {
      comments: false,
    },
  });

  if (result.error) {
    throw result.error;
  }

  return result.code || code;
}

function obfuscateJs(code) {
  const obfuscated = JavaScriptObfuscator.obfuscate(code, {
    compact: true,
    controlFlowFlattening: false,
    deadCodeInjection: false,
    debugProtection: false,
    disableConsoleOutput: false,
    identifierNamesGenerator: "hexadecimal",
    numbersToExpressions: false,
    renameGlobals: false,
    selfDefending: false,
    simplify: true,
    splitStrings: false,
    stringArray: true,
    stringArrayRotate: true,
    stringArrayShuffle: true,
    stringArrayWrappersCount: 1,
    stringArrayThreshold: 0.75,
    transformObjectKeys: false,
    unicodeEscapeSequence: false,
  });

  return obfuscated.getObfuscatedCode();
}

function isInlineScriptExecutable(attributes) {
  if (/\bsrc\s*=/i.test(attributes)) {
    return false;
  }

  const typeMatch = attributes.match(/\btype\s*=\s*(['"])(.*?)\1/i);
  const typeValue = typeMatch ? typeMatch[2].trim().toLowerCase() : "";

  if (!typeValue) {
    return true;
  }

  if (typeValue === "module") {
    return true;
  }

  return [
    "text/javascript",
    "application/javascript",
    "text/ecmascript",
    "application/ecmascript",
  ].includes(typeValue);
}

function inlineScriptMode(attributes) {
  const typeMatch = attributes.match(/\btype\s*=\s*(['"])(.*?)\1/i);
  const typeValue = typeMatch ? typeMatch[2].trim().toLowerCase() : "";
  return typeValue === "module" ? "module" : "classic";
}

async function transformHtml(source) {
  const inlineScriptReports = [];
  let inlineScriptIndex = 0;

  const withInlineTransforms = await (async () => {
    let rebuilt = "";
    let lastIndex = 0;
    const scriptRegex = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;

    for (const match of source.matchAll(scriptRegex)) {
      const start = match.index ?? 0;
      const end = start + match[0].length;
      const attributes = match[1] || "";
      const scriptBody = match[2] || "";

      rebuilt += source.slice(lastIndex, start);

      if (!isInlineScriptExecutable(attributes)) {
        inlineScriptReports.push({
          index: inlineScriptIndex++,
          mode: "skipped",
          reason: "non_executable_or_external_script",
          original_bytes: Buffer.byteLength(scriptBody, "utf8"),
          transformed_bytes: Buffer.byteLength(scriptBody, "utf8"),
        });
        rebuilt += match[0];
        lastIndex = end;
        continue;
      }

      const scriptMode = inlineScriptMode(attributes);
      let transformedBody = scriptBody;
      let transformType = "minified";

      if (scriptMode === "module") {
        transformedBody = await minifyInlineJs(scriptBody, true);
        transformType = "minified_module";
      } else {
        const minifiedBody = await minifyInlineJs(scriptBody, false);
        transformedBody = obfuscateJs(minifiedBody);
        transformType = "obfuscated_classic";
      }

      inlineScriptReports.push({
        index: inlineScriptIndex++,
        mode: scriptMode,
        transform: transformType,
        original_bytes: Buffer.byteLength(scriptBody, "utf8"),
        transformed_bytes: Buffer.byteLength(transformedBody, "utf8"),
      });

      rebuilt += `<script${attributes}>${transformedBody}</script>`;
      lastIndex = end;
    }

    rebuilt += source.slice(lastIndex);
    return rebuilt;
  })();

  const minifiedHtml = await minify(withInlineTransforms, {
    collapseWhitespace: true,
    conservativeCollapse: true,
    removeComments: true,
    removeRedundantAttributes: false,
    removeScriptTypeAttributes: false,
    removeStyleLinkTypeAttributes: false,
    caseSensitive: true,
    minifyCSS: (text) => minifyCss(text),
    minifyJS: false,
  });

  return {
    code: minifiedHtml,
    inline_scripts: inlineScriptReports,
  };
}

function transformCss(source) {
  return minifyCss(source);
}

function transformJs(source) {
  return obfuscateJs(source);
}

async function main() {
  const [targetDir] = process.argv.slice(2);

  if (!targetDir) {
    console.error("Usage: node scripts/transform_web_assets.js <target-dir>");
    process.exit(1);
  }

  const resolvedTarget = path.resolve(targetDir);
  if (!fs.existsSync(resolvedTarget) || !fs.statSync(resolvedTarget).isDirectory()) {
    console.error(`Target directory does not exist or is not a directory: ${resolvedTarget}`);
    process.exit(1);
  }

  const files = collectFiles(resolvedTarget);
  const report = {
    target_dir: resolvedTarget,
    transformed_at: new Date().toISOString(),
    html_files: [],
    css_files: [],
    js_files: [],
    skipped_files: [],
  };

  for (const filePath of files) {
    const extension = path.extname(filePath).toLowerCase();
    const relativePath = path.relative(resolvedTarget, filePath);
    const source = fs.readFileSync(filePath, "utf8");
    let transformed = null;
    let bucket = null;
    let extraReport = {};

    if (extension === ".html") {
      const htmlResult = await transformHtml(source);
      transformed = htmlResult.code;
      bucket = "html_files";
      extraReport = {
        inline_scripts: htmlResult.inline_scripts,
      };
    } else if (extension === ".css") {
      transformed = transformCss(source);
      bucket = "css_files";
    } else if (extension === ".js") {
      transformed = transformJs(source);
      bucket = "js_files";
    } else {
      report.skipped_files.push(relativePath);
      continue;
    }

    fs.writeFileSync(filePath, transformed, "utf8");
    report[bucket].push({
      path: relativePath,
      original_bytes: Buffer.byteLength(source, "utf8"),
      transformed_bytes: Buffer.byteLength(transformed, "utf8"),
      ...extraReport,
    });
  }

  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});