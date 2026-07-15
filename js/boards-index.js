/* ===== reanotes 板块索引 =====
 * 新增一个研究板块的步骤：
 *   1. 在 js/boards/ 下复制 replearning.js，改名为 <boardId>.js，
 *      把其中 BOARD_DATA['replearning'] 改为 BOARD_DATA['<boardId>']，
 *      并替换 home / navTree / content 为你板块的内容。
 *   2. 在下面 BOARDS 数组里加一行即可（顺序即展示顺序）。
 * 注意：每个板块文件必须整体包在 IIFE 内（如 (function () { ... })();），
 *       否则多文件顶层 const（HOME_GRID / NAV_TREE / CONTENT 等）会重复声明，
 *       导致第二个板块加载失败。
 */
const BOARDS = [
  {
    id: 'replearning',
    name: '表征学习',
    icon: '🧠',
    desc: '从自编码器到对比学习，从线性降维到深度非线性',
    accent: '#4f46e5',
  },
  {
    id: 'dlproject',
    name: '深度学习工程',
    icon: '🛠️',
    desc: '从问题定义到部署监控的完整项目流程',
    accent: '#1d72b8',
  },
  {
    id: 'dlresearch',
    name: '深度学习科研',
    icon: '🔬',
    desc: '科研主战场：架构、表示、训练与调优',
    accent: '#0d9488',
  },
  {
    id: 'literature',
    name: '文献索引',
    icon: '📚',
    desc: '学术论文索引与会议期刊导航',
    accent: '#8b5cf6',
  },
];
