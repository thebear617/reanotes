import { viteBundler } from "@vuepress/bundler-vite";
import { defineUserConfig } from "vuepress";

import { theme } from "./theme.js";

export default defineUserConfig({
  base: process.env.SITE_BASE || "/",
  lang: "zh-CN",
  title: "ReaNotes",
  description: "按研究板块组织的科研笔记总站",
  dest: "./dist",
  pagePatterns: [
    "**/*.md",
    "!**/*.snippet.md",
    "!**/TODO.md",
    "!.vuepress",
    "!node_modules",
  ],
  bundler: viteBundler(),
  theme,
});
