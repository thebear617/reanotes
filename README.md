# reanotes · 科研笔记总站

> 个人科研笔记的知识索引。表征学习只是其中一个板块，可容纳任意多个研究板块。

在线地址：http://rea.thebear617.cn/ （GitHub Pages 备用：https://thebear617.github.io/reanotes/）

## 这是什么？

这是一个**多板块的个人科研笔记站**。首页是板块总览仪表盘，每个板块是一块独立的知识域（例如「表征学习」），内部用可折叠的卡片组织理解脉络。新增研究主题 = 新增一个板块，零侵入。

## 信息架构

```
reanotes 首页（板块总览仪表盘）
├── 🧠 表征学习   (replearning)   ← 现有全部表征学习内容整体迁入
├── 📚 板块二      (待添加)
├── 🔬 板块三      (待添加)
└── …… 后续任意新增
```

- **首页（总览）**：列出所有板块卡片，点击进入
- **进入某板块后**：顶栏板块切换器可一点换板块；左侧是该板块自己的导航；面包屑「🏠 首页」回到该板块首页；点顶栏站名「reanotes」回到总览
- **路由**：用 URL hash，`#replearning` 进板块首页，`#replearning/self-supervised` 直接定位某页，空 hash 为总览

## 文件结构

```
├── index.html              # 页面入口（标题、顶栏、板块切换器容器）
├── content/
│   └── tabs/
│       ├── README.md                 # Tab 与磁盘目录映射
│       └── replearning/              # 顶栏 Tab：表征学习
│           ├── pages.json            # 板块目录、顺序和卡片排列
│           └── boards/
│               └── <board>/*.md      # 各板块卡片正文（唯一内容源）
├── css/
│   └── style.css           # 所有样式（靛青色系 + 侧边栏布局 + 仪表盘/切换器）
├── js/
    ├── boards-index.js     # 板块索引 BOARDS：决定有哪些板块、顺序、配色
    ├── boards/
    │   ├── replearning.js        # 表征学习导航、首页和装配逻辑
    │   └── replearning.cards.js  # Markdown 编译生成物，请勿手改
    └── app.js              # 渲染引擎：总览、板块切换、侧栏、卡片折叠、响应式
└── scripts/
    ├── build-cards.py      # Markdown → 页面数据编译器
    └── install-hooks.sh    # 安装仓库内的 pre-commit hook
```

## 如何添加新内容

### 在已有板块里加页面

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

仓库会把 `core.hooksPath` 设置为 `.githooks`。以后提交 Markdown 或编译脚本时，`pre-commit` 会自动：

1. 检查相关文件是否还有未暂存修改；
2. 运行 `python3 scripts/build-cards.py`；
3. 暂存 `js/boards/replearning.cards.js`；
4. 用 `--check` 确认生成物与 Markdown 一致。

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
- **GitHub Pages**：仓库名 `reanotes`，`git push origin main` 后自动构建，地址 `https://thebear617.github.io/reanotes/`。
- **Vercel（自定义域名 `rea.thebear617.cn`）**：在 Vercel 导入 `thebear617/reanotes` 仓库并绑定该域名（DNS 已指向 Vercel），随 `main` 自动部署。

```bash
git push origin main
```

## 许可证

MIT
