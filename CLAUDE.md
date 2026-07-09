# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目性质

纯静态站点：HTML + CSS + 原生 JavaScript，**无构建步骤、无依赖、无测试、无 linter**。
部署在 GitHub Pages（`https://thebear617.github.io/reanotes/`），推送到 `main` 自动发布。
**多板块**结构：表征学习只是其中一个板块，站点可容纳任意多个研究板块。

## 运行方式

任意静态服务器即可，无需安装依赖：

```bash
python3 -m http.server 8000        # 或
npx serve .
```

打开 `http://localhost:8000`。

## 架构（数据驱动 · 多板块）

整个站点是**单页应用 + 客户端渲染**，数据按板块拆分，渲染引擎在 `js/app.js`。

```
index.html           # 骨架：顶栏（含板块切换器）+ 侧栏容器 + 主内容区；依次加载下方三个脚本
css/style.css        # 单一样式表（设计 token 在 :root，靛青 #4f46e5 / 深蓝灰 #0f172a + 仪表盘/切换器样式）
js/boards-index.js   # 板块索引：全局 BOARDS 数组（决定有哪些板块、顺序、accent 配色）
js/boards/replearning.js  # 表征学习板块数据，包装为 BOARD_DATA['replearning'] = { home, navTree, content }
js/app.js            # 渲染层：IIFE；渲染总览仪表盘、板块切换、侧栏、内容页、卡片折叠、响应式
```

**关键约定**：
- 加载顺序：先 `boards-index.js`（定义 `BOARDS`）→ 再各板块 `js/boards/<id>.js`（向全局 `BOARD_DATA` 注册）→ 最后 `app.js`
- `BOARD_DATA[id] = { home, navTree, content }`：
  - `home`：板块首页（含 `title` / `desc` / `gridCards` / `quickRef` / `recentUpdates`）
  - `navTree`：该板块侧栏结构（`{id, icon, label}` 叶节点，或带 `children` 的父节点，`{type:'divider'}` 分隔条）
  - `content`：页面正文，**键 id 必须与 `navTree` 中的 id 对应**
- 路由用 URL hash（两级）：`#` 空=总览仪表盘，`#<boardId>`=板块首页，`#<boardId>/<pageId>`=某页；刷新或外链可直接定位（`app.js` 监听 `hashchange`）
- 内容卡片支持 HTML body（`body` 字段就是 HTML 字符串）
- 详情见 `README.md` 的「如何添加新内容」一节

## 添加内容的最小流程

### 在已有板块加页面
1. 在对应 `js/boards/<id>.js` 的 `navTree` 加入口
2. 在同文件 `content` 对象加对应页面（`title` / `desc` / `cards` 数组）
3. 卡片 schema：`{icon, title, tags, expanded, body}`，`body` 是 HTML

### 新增一个研究板块
1. 复制 `js/boards/replearning.js` 为 `js/boards/<newId>.js`，把 `BOARD_DATA['replearning']` 改为 `BOARD_DATA['<newId>']`，替换数据
2. 在 `js/boards-index.js` 的 `BOARDS` 数组加一行
3. 在 `index.html` 里加一行 `<script src="js/boards/<newId>.js"></script>`

## CSS 设计 token

`css/style.css` 的 `:root` 集中定义了所有色/圆角/阴影。改色先改这里。
颜色家族：`--accent`（靛青）/ `--dark`/`--darker`（深蓝灰）/ `--green` / `--blue` / `--amber` / `--red`，每色配 `--xxx-bg` 浅色背景。
板块卡片/切换器可用各自 `accent` 自定义点缀色（在 `BOARDS` 里配，行内 `--accent` 生效）。

## 响应式

断点在 820px。窄屏下侧栏转为 fixed + 滑出 + 遮罩（`.sidebar.open` + `.sidebar-backdrop`）；`Esc` 关闭（`app.js` 已绑定）。顶栏板块切换器在窄屏横向滚动。

## Git 提交风格

历史 commit 用中文 `type: 描述` 格式（chore / fix / feat / init）。新增内容建议用 `feat:`，样式调整 `chore:` 或 `style:`。