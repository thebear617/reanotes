import { arraySidebar } from "vuepress-theme-hope";

export default arraySidebar([
  "",
  {
    text: "科研视角总览",
    icon: "binoculars",
    prefix: "overview/",
    collapsible: true,
    children: ["根本区别", "科研主战场一览", "怎么读这个板块"],
  },
  {
    text: "问题定义",
    icon: "bullseye",
    prefix: "f-problem/",
    collapsible: true,
    children: ["这个 gap 存在吗？", "能不能重新表述", "指标本身合理吗", "回链"],
  },
  {
    text: "架构探索",
    icon: "diagram-project",
    prefix: "f-arch/",
    collapsible: true,
    children: [
      "设计新模块 _ 层",
      "消融搞清_为什么有效",
      "从假设到验证",
      "可解释性",
      "回链",
    ],
  },
  {
    text: "特征与表示",
    icon: "shapes",
    prefix: "f-rep/",
    collapsible: true,
    children: [
      "更好的输入表示",
      "自监督 _ 预训练任务设计",
      "数据增强创新",
      "回链",
    ],
  },
  {
    text: "训练方法",
    icon: "fire",
    prefix: "f-train/",
    collapsible: true,
    children: ["新的损失函数设计", "新的优化策略", "训练稳定性根因", "回链"],
  },
  {
    text: "调优与验证",
    icon: "flask",
    prefix: "f-tune/",
    collapsible: true,
    children: ["消融是灵魂", "公平对比", "多数据集 _ 多 seed", "回链"],
  },
  {
    text: "科研浅尝辄止",
    icon: "screwdriver-wrench",
    prefix: "f-shallow/",
    collapsible: true,
    children: [
      "数据收集 _ 清洗的工程细节",
      "部署、压缩、上线监控",
      "Pipeline 工程化",
    ],
  },
  {
    text: "科研 vs 工程",
    icon: "scale-balanced",
    prefix: "f-vs/",
    collapsible: true,
    children: [
      "工程：效果好不好",
      "科研：为什么好，能否推广",
      "一个闭环的差异",
    ],
  },
]);
