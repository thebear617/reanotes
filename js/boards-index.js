/* ===== reanotes 板块索引 =====
 * 新增一个研究板块的步骤：
 *   1. 在 js/boards/ 下复制 replearning.js，改名为 <boardId>.js，
 *      把其中 BOARD_DATA['replearning'] 改为 BOARD_DATA['<boardId>']，
 *      并替换 home / navTree / content 为你板块的内容。
 *   2. 在下面 BOARDS 数组里加一行即可（顺序即展示顺序）。
 */
const BOARDS = [
  {
    id: 'replearning',
    name: '表征学习',
    icon: '🧠',
    desc: '从自编码器到对比学习，从线性降维到深度非线性',
    accent: '#4f46e5',
  },
  // 示例（取消注释并替换即可启用新板块）：
  // {
  //   id: 'topic-xxx',
  //   name: '板块二',
  //   icon: '🔬',
  //   desc: '一句话描述这个研究板块',
  //   accent: '#0f6e56',
  // },
];
