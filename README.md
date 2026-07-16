# reanotes · 科研笔记总站

> 个人科研笔记的知识索引。表征学习只是其中一个板块，可容纳任意多个研究板块。

在线地址：http://rea.thebear617.cn/ （GitHub Pages 备用：https://thebear617.github.io/reanotes/）

## 这是什么？

这是一个**多板块的个人科研笔记站**。项目正在从原生 JS 卡片站迁移到与 JavaGuide 相同的 VuePress 2 + Vite + Vue 3 + Theme Hope 架构。新内容以 `docs/` 下的 Markdown 为唯一内容源，并按顶栏 Tab 和板块分目录组织。

## 信息架构

```
ReaNotes
├── 表征学习       /replearning/
├── 深度学习项目   /dlproject/
├── 深度学习研究   /dlresearch/
└── 文献库         /literature/
```

- **首页**：四个研究 Tab 的入口。
- **顶栏**：用于切换研究 Tab。
- **侧栏**：每个 Tab 拥有独立的板块和 Markdown 文档树。
- **路由**：使用真实路径，例如 `/replearning/foundation/linear-vs-nonlinear.html`。

## 文件结构

```
├── docs/                         # 新站 Markdown 内容源
│   ├── .vuepress/
│   │   ├── config.ts             # VuePress 与 Vite 配置
│   │   ├── navbar.ts             # 顶栏 Tab
│   │   ├── sidebar/              # 各 Tab 的侧栏配置
│   │   └── theme.ts              # Theme Hope 配置
│   ├── replearning/
│   ├── dlproject/
│   ├── dlresearch/
│   └── literature/
├── package.json                  # pnpm 命令和依赖
├── .husky/pre-commit             # 提交前检查
├── .github/workflows/test.yml    # CI 构建验证
├── index.html                    # 迁移期间保留的旧站入口
├── content/                      # 旧站 Markdown 内容源，待逐步迁移
├── js/                           # 旧站数据和渲染代码，待切换后移除
└── scripts/build-cards.py        # 旧站内容编译器，迁移期间继续校验
```

## 如何添加新内容

### 在新站里加页面

1. 在 `docs/<tab>/<board>/` 下新建 Markdown 文件。
2. 在 `docs/.vuepress/sidebar/` 对应的侧栏文件中登记页面。
3. 执行 `pnpm dev` 本地编辑和预览。
4. 提交前执行 `pnpm lint && pnpm build`。

### 旧站内容

表征学习正文统一编辑 `content/tabs/replearning/`，不要手改生成的
`js/boards/replearning.cards.js`：

1. 找到顶栏 Tab 目录 `content/tabs/replearning/`。
2. 在 `boards/<board>/` 下新建一张 `.md` 卡片。
3. 在 `content/tabs/replearning/pages.json` 登记板块和卡片顺序。
4. 如需新导航入口，再修改 `js/boards/replearning.js` 的 `NAV_TREE`。
5. 执行 `python3 scripts/build-cards.py` 生成页面数据。
6. 用 `python3 -m http.server 8000` 本地预览。

例如：

```markdown
---
icon: 🏛️
title: ImageNet 预训练范式
tags: [经典]
expanded: true
---

在 ImageNet 上训练一个分类网络，去掉最后的分类头，
把倒数第二层的特征向量当作通用表示。
```

Markdown 支持标题、列表、表格、引用、代码、链接、图片和 KaTeX 公式；复杂表格或布局可直接嵌入 HTML。编译后内容仍随 JS 一并发出，无运行时网络请求。

目前只有“表征学习”完成 Markdown 化；其他三个顶栏 Tab 仍使用各自的
`js/boards/<tabId>.js`。具体状态见 `content/tabs/README.md`。

### 提交前自动编译

首次克隆后执行一次：

```bash
./scripts/install-hooks.sh
```

依赖安装时 Husky 会把 `core.hooksPath` 设置为 `.husky/_`。以后提交时，`pre-commit` 会自动：

1. 用 `python3 scripts/build-cards.py --check` 确认旧站生成物仍与内容源一致；
2. 用 Prettier 格式化暂存文件；
3. 用 markdownlint 检查暂存的 Markdown。

也可以手动检查：

```bash
python3 scripts/build-cards.py --check
```

### 新增一个顶栏 Tab

1. 复制 `js/boards/replearning.js` 为 `js/boards/<tabId>.js`，把里面 `BOARD_DATA['replearning']` 改为 `BOARD_DATA['<tabId>']`，替换 `home` / `navTree` / `content`
2. 在 `js/boards-index.js` 的 `BOARDS` 数组加一行：
   ```js
   { id: 'topic-xxx', name: '板块二', icon: '🔬', desc: '一句话描述', accent: '#0f6e56' },
   ```
3. 在 `index.html` 里 `<script src="js/boards/replearning.js"></script>` 下方加一行 `<script src="js/boards/<tabId>.js"></script>`
4. 如果该 Tab 使用 Markdown，再建立 `content/tabs/<tabId>/boards/` 和对应的内容目录，并为它接入编译生成物

## 设计语言

- **主色调**：深蓝灰（`#0f172a`）+ 靛青（`#4f46e5`），各板块可用 `accent` 自定义点缀色
- **布局**：顶栏板块切换器 + 左侧固定导航 + 右侧内容区，知识库风格
- **卡片系统**：可折叠展开，适合层次化阅读
- **响应式**：窄屏时侧边栏转为滑出 + 遮罩

## 部署

本仓库**双托管**：

- **GitHub Pages**：`.github/workflows/deploy.yml` 会使用 `/reanotes/` 基础路径构建并发布 `dist/`，地址 `https://thebear617.github.io/reanotes/`。首次切换时需要在仓库 Settings → Pages 中把 Source 改成 **GitHub Actions**。
- **Vercel（自定义域名 `rea.thebear617.cn`）**：`vercel.json` 会在根路径构建并发布 `dist/`，随 `main` 自动部署。

部署前可在本地执行：

```bash
pnpm lint
pnpm build
```

```bash
git push origin main
```

## 许可证

MIT
