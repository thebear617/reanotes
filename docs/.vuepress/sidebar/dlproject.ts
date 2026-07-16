import { arraySidebar } from "vuepress-theme-hope";

export default arraySidebar([
  "",
  {
    text: "流程全景",
    icon: "map",
    prefix: "overview/",
    collapsible: true,
    children: ["八阶段一览", "两个视角：纵切 vs 横切", "怎么读这个板块"],
  },
  {
    text: "1 问题定义",
    icon: "bullseye",
    prefix: "p1/",
    collapsible: true,
    children: ["明确任务类型", "确定评估指标", "评估可行性"],
  },
  {
    text: "2 数据准备",
    icon: "database",
    prefix: "p2/",
    collapsible: true,
    children: [
      "收集 _ 爬取 _ 标注",
      "数据清洗",
      "探索性分析（EDA）",
      "划分 train _ val _ test",
    ],
  },
  {
    text: "3 特征工程",
    icon: "sliders",
    prefix: "p3/",
    collapsible: true,
    children: [
      "归一化 _ 标准化",
      "数据增强",
      "Tokenization",
      "构建 DataLoader _ Pipeline",
    ],
  },
  {
    text: "4 模型设计",
    icon: "diagram-project",
    prefix: "p4/",
    collapsible: true,
    children: ["从简单 baseline 起步", "选择架构", "确定损失函数"],
  },
  {
    text: "5 训练",
    icon: "fire",
    prefix: "p5/",
    collapsible: true,
    children: [
      "设置超参数",
      "训练循环与监控",
      "早停（early stopping）",
      "实验追踪",
    ],
  },
  {
    text: "6 调优",
    icon: "wand-magic-sparkles",
    prefix: "p6/",
    collapsible: true,
    children: ["超参数搜索", "错误分析", "正则化"],
  },
  {
    text: "7 评估",
    icon: "clipboard-check",
    prefix: "p7/",
    collapsible: true,
    children: ["测试集纪律", "消融实验（ablation）", "鲁棒性与公平性"],
  },
  {
    text: "8 部署监控",
    icon: "rocket",
    prefix: "p8/",
    collapsible: true,
    children: ["压缩 _ 量化", "部署为 API _ 集成产品", "监控漂移", "反馈闭环"],
  },
]);
