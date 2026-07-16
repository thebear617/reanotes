import { arraySidebar } from "vuepress-theme-hope";

export default arraySidebar([
  "",
  { text: "文献索引", icon: "book", link: "papers" },
  { text: "学术会议与期刊", icon: "graduation-cap", link: "venues" },
  {
    text: "论文全文",
    icon: "file-lines",
    prefix: "translations/attention-is-all-you-need/",
    children: [
      { text: "Attention Is All You Need（中文）", link: "" },
      { text: "Attention Is All You Need（原文）", link: "original" },
    ],
  },
]);
