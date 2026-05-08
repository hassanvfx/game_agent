#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { minify } = require("html-minifier-terser");
const CleanCSS = require("clean-css");
const terser = require("terser");

async function main() {
  const [inputPath, outputPath, profile = "minify"] = process.argv.slice(2);

  if (!inputPath || !outputPath) {
    console.error("Usage: node scripts/minify_html.js <input> <output> [profile]");
    process.exit(1);
  }

  const html = fs.readFileSync(inputPath, "utf8");
  const scriptPlaceholders = [];
  const htmlWithScriptPlaceholders = html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, (match) => {
    const placeholder = `___GAME_OBFUSCATOR_SCRIPT_${scriptPlaceholders.length}___`;
    scriptPlaceholders.push(match);
    return placeholder;
  });

  const cssMinifier =
    profile === "max"
      ? new CleanCSS({ level: { 1: { all: true }, 2: { all: true } } })
      : new CleanCSS({ level: 2 });

  const minifiedHtml = await minify(htmlWithScriptPlaceholders, {
    collapseWhitespace: true,
    conservativeCollapse: true,
    removeComments: true,
    removeRedundantAttributes: false,
    removeScriptTypeAttributes: false,
    removeStyleLinkTypeAttributes: false,
    minifyCSS: (text) => cssMinifier.minify(text).styles,
    minifyJS: async (text) => {
      const terserOptions =
        profile === "max"
          ? {
              compress: {
                passes: 3,
                pure_getters: true,
                unsafe_math: true,
                unsafe_comps: true,
                drop_console: false,
              },
              mangle: {
                toplevel: true,
              },
              format: {
                comments: false,
              },
            }
          : profile === "mangle"
            ? {
                compress: {
                  passes: 2,
                },
                mangle: {
                  toplevel: false,
                },
                format: {
                  comments: false,
                },
              }
            : {
                compress: true,
                mangle: false,
                format: {
                  comments: false,
                },
              };

      const result = await terser.minify(text, terserOptions);
      if (result.error) {
        throw result.error;
      }
      return result.code || text;
    },
  });

  const minified = scriptPlaceholders.reduce(
    (currentHtml, scriptBlock, index) =>
      currentHtml.replace(
        `___GAME_OBFUSCATOR_SCRIPT_${index}___`,
        scriptBlock.replace(/\s+type=(["'])module\1(?=[^>]*\ssrc=)(?=[^>]*\stype=(["'])module\2)/i, ""),
      ),
    minifiedHtml,
  );

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, minified, "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});