# ReaNotes · 科研笔记总站

> 按研究板块组织、以 Markdown 为唯一内容源的科研笔记站。

- 主站：[rea.thebear617.cn](https://rea.thebear617.cn/)
- GitHub Pages：[thebear617.github.io/reanotes](https://thebear617.github.io/reanotes/)
- 当前版本：`v0.4.2`（[更新记录](CHANGELOG.md)）

## 技术架构

项目使用 VuePress 2、Vite、Vue 3 和 Theme Hope，通过 pnpm 管理依赖。所有可编辑内容都位于 `docs/`，构建产物输出到 `dist/`。

```text
docs/
├── .vuepress/       # 站点、主题、顶栏和侧栏配置
├── replearning/     # 表征学习
├── dlproject/       # 深度学习项目
├── dlresearch/      # 深度学习研究
└── literature/      # 文献索引、会议期刊和论文全文
```

## 本地开发

首次使用先安装依赖：

```bash
pnpm install
```

启动本地站点：

```bash
pnpm dev
```

打开终端显示的地址，通常是 `http://localhost:8080/`。修改 `docs/` 中的 Markdown 后页面会自动更新。

## 添加内容

1. 在 `docs/<tab>/<board>/` 中创建 Markdown 文件。
2. 在 `docs/.vuepress/sidebar/` 对应的侧栏文件中登记页面。
3. 使用 `pnpm dev` 预览。
4. 提交前运行 `pnpm lint && pnpm build`。

常用 frontmatter：

```yaml
---
title: 页面标题
category:
  - 所属板块
tag:
  - 标签
---
```

## 提交检查

安装依赖时 Husky 会自动配置 Git hook。每次提交前，nano-staged 会格式化暂存文件并检查 Markdown。

也可以手动执行：

```bash
pnpm lint
pnpm build
```

## 部署

- GitHub Pages：推送 `main` 后，由 `.github/workflows/deploy.yml` 使用 `/reanotes/` 基础路径构建并发布。
- Vercel：`vercel.json` 在根路径构建并发布 `dist/`，绑定自定义域名 `rea.thebear617.cn`。

```bash
git push origin main
```

## 许可证

MIT
