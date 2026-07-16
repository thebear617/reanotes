import { arraySidebar } from "vuepress-theme-hope";

export default arraySidebar([
  "",
  { text: "基础知识", icon: "seedling", link: "foundation/" },
  { text: "监督表示学习", icon: "graduation-cap", link: "supervised/" },
  { text: "自监督表示学习", icon: "rotate", link: "self-supervised/" },
  {
    text: "传统无监督表示学习",
    icon: "circle-nodes",
    link: "unsupervised/",
  },
  {
    text: "半监督、弱监督表示学习",
    icon: "tags",
    link: "semi-supervised/",
  },
  { text: "度量学习", icon: "ruler-combined", link: "metric/" },
  {
    text: "迁移表示学习",
    icon: "arrow-right-arrow-left",
    link: "transfer/",
  },
  { text: "多任务表示学习", icon: "list-check", link: "multitask/" },
  { text: "架构范式对照", icon: "sitemap", link: "architecture/" },
  { text: "理解笔记", icon: "note-sticky", link: "notes/" },
]);
