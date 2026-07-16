# Markdown 内容目录

本目录按界面层级组织内容：

```text
tabs/<tab-id>/boards/<board-id>/*.md
```

- `tab-id` 对应顶栏 Tab，也是 `js/boards-index.js` 中的 `BOARDS[].id`。
- `board-id` 对应该 Tab 内的内容板块，也是路由中的页面 id。
- `pages.json` 位于 Tab 根目录，声明板块元数据、顺序和卡片文件顺序。
- `.md` 是正文唯一来源；`js/boards/*.cards.js` 是生成物，不手动编辑。

当前 Markdown 化状态：

| Tab | id | 内容状态 |
| --- | --- | --- |
| 表征学习 | `replearning` | 已迁入 `tabs/replearning/boards/` |
| 深度学习工程 | `dlproject` | 仍由 `js/boards/dlproject.js` 管理 |
| 深度学习科研 | `dlresearch` | 仍由 `js/boards/dlresearch.js` 管理 |
| 文献索引 | `literature` | 仍由 `js/boards/literature.js` 管理 |

