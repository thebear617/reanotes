import { arraySidebar } from "vuepress-theme-hope";

export default arraySidebar([
  "",
  {
    text: "基础知识",
    icon: "seedling",
    prefix: "foundation/",
    collapsible: true,
    children: ["representation-learning-model", "linear-vs-nonlinear"],
  },
]);
