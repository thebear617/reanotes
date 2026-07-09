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
├── css/
│   └── style.css           # 所有样式（靛青色系 + 侧边栏布局 + 仪表盘/切换器）
└── js/
    ├── boards-index.js     # 板块索引 BOARDS：决定有哪些板块、顺序、配色
    ├── boards/
    │   └── replearning.js  # 表征学习板块数据（home / navTree / content）
    └── app.js              # 渲染引擎：总览、板块切换、侧栏、卡片折叠、响应式
```

## 如何添加新内容

### 在已有板块里加页面

所有内容在对应板块的 `js/boards/<boardId>.js`：

1. 在 `navTree` 数组加入口（叶节点 `{id, icon, label}` 或带 `children` 的父节点；也可用 `{type: 'divider'}` 分隔条）
2. 在 `content` 对象加对应页面（`title` / `desc` / `cards` 数组）
3. 卡片 schema：`{icon, title, tags, expanded, body}`，`body` 是 HTML
4. 首页 `HOME_GRID` / `HOME_UPDATES` / `HOME_QUICKREF` 是板块首页的独立列表

### 新增一个研究板块

1. 复制 `js/boards/replearning.js` 为 `js/boards/<boardId>.js`，把里面 `BOARD_DATA['replearning']` 改为 `BOARD_DATA['<boardId>']`，替换 `home` / `navTree` / `content`
2. 在 `js/boards-index.js` 的 `BOARDS` 数组加一行：
   ```js
   { id: 'topic-xxx', name: '板块二', icon: '🔬', desc: '一句话描述', accent: '#0f6e56' },
   ```
3. 在 `index.html` 里 `<script src="js/boards/replearning.js"></script>` 下方加一行 `<script src="js/boards/<boardId>.js"></script>`
4. 刷新即可，无需构建

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
