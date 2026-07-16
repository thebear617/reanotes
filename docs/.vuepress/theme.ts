import { hopeTheme } from "vuepress-theme-hope";

import navbar from "./navbar.js";
import sidebar from "./sidebar/index.js";

export const theme = hopeTheme({
  hostname: "https://rea.thebear617.cn",
  author: {
    name: "ReaNotes",
  },
  repo: "https://github.com/thebear617/reanotes",
  docsDir: "docs",
  navbar,
  sidebar,
  displayFooter: true,
  footer: "科研笔记 · 持续整理",
  markdown: {
    align: true,
    codeTabs: true,
    gfm: true,
    math: {
      type: "mathjax",
    },
    mermaid: true,
    tasklist: true,
  },
  plugins: {
    blog: false,
    feed: {
      atom: true,
      json: true,
      rss: true,
    },
    sitemap: true,
  },
});
