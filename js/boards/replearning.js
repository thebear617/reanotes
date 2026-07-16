(function () {
/* ===== 首页数据 ===== */
const HOME_GRID = [
  { id: 'foundation',       icon: '📜', title: '基础知识',       desc: '表征学习的数学模型与研究目的' },
  { id: 'overview',         icon: '🔭', title: '发展史',       desc: '表征学习发展里程碑' },
  { id: 'architecture',     icon: '🏗️', title: '架构范式对照',   desc: 'AE vs U-Net 设计哲学' },
  { id: 'notes',            icon: '📝', title: '理解笔记',       desc: '关键洞察和核心速记' },
  { id: 'self-supervised',  icon: '🔄', title: '自监督学习',     desc: '生成式 · 对比式 · 非对比式' },
  { id: 'supervised',       icon: '🏛️', title: '监督表示学习',   desc: 'ImageNet 预训练、线性探针' },
  { id: 'metric',           icon: '📏', title: '度量学习',       desc: 'Triplet Loss、ArcFace' },
];

const HOME_UPDATES = [
  { date: '2026-07-11', text: '新增基础知识：数学模型与研究目的', id: 'foundation' },
  { date: '2026-06-30', text: '创建表征学习发展史时间轴',        id: 'overview' },
  { date: '2026-06-30', text: '自监督学习三大范式',            id: 'self-supervised' },
  { date: '2026-06-30', text: '架构范式对照：AE vs U-Net',     id: 'architecture' },
  { date: '2026-06-30', text: '理解笔记沉淀',                  id: 'notes' },
];

const HOME_QUICKREF = [
  { label: '生成式',     slogan: '"把砸烂的东西恢复原样"',          models: 'AE · MAE · BERT' },
  { label: '对比式',     slogan: '"把一样的拉近、不一样的推开"',    models: 'SimCLR · MoCo · CLIP' },
  { label: '非对比式',   slogan: '"两个分支输出相关但不能坍塌"',    models: 'BYOL · Barlow Twins · DINO' },
];

/* ===== 导航树 ===== */
const NAV_TREE = [
  { id: 'foundation',  icon: '📜', label: '基础知识' },
  { id: 'overview',    icon: '🔭', label: '发展史' },
  { id: 'architecture',     icon: '🏗️', label: '架构范式对照' },
  { id: 'notes',            icon: '📝', label: '理解笔记' },
  { id: 'div1',        type: 'divider' },
  {
    id: 'cat-supervision', icon: '📐', label: '按监督信号',
    children: [
      { id: 'unsupervised',      label: '传统无监督表示学习' },
      { id: 'supervised',        label: '监督表示学习' },
      { id: 'self-supervised',   label: '自监督表示学习' },
      { id: 'semi-supervised',   label: '半监督、弱监督表示学习' },
    ]
  },
  {
    id: 'cat-objective', icon: '🎯', label: '按学习目标',
    children: [
      { id: 'metric',       label: '度量学习' },
      { id: 'transfer',     label: '迁移表示学习' },
      { id: 'multitask',    label: '多任务表示学习' },
    ]
  },
];

/* ===== 内容数据 ===== */
const CONTENT = {};

CONTENT['home'] = {
  type: 'home',
  title: '表征学习 · 理解图谱',
  desc: '从自编码器到对比学习，从线性降维到深度非线性——一个持续演进的知识索引。所有内容均可折叠展开，点击即可浏览。',
  gridCards: HOME_GRID,
  recentUpdates: HOME_UPDATES,
  quickRef: HOME_QUICKREF,
};

/* ─── 发展史 ─── */
CONTENT['overview'] = {
  title: '🔭 发展史',
  desc: '表征学习从手工特征到深度自监督的演进。每个节点都是一个重要的转折点或里程碑。',
  timeline: [
    {
      date: '2012',
      title: '表征学习综述 + ICLR 诞生',
      desc: 'Bengio 发表综述《Representation Learning: A Review and New Perspectives》，提出十大先验框架；同年与 LeCun 创办第一届 ICLR（International Conference on Learning Representations），会议名称直指"表征学习"。',
      tags: ['奠基', 'Bengio'],
    },
    {
      date: '2012',
      title: 'AlexNet — 深度特征工程的开端',
      desc: 'Krizhevsky, Sutskever, Hinton 的 AlexNet 在 ImageNet 上大幅刷新纪录。虽然本质是监督分类，但它证明深度 CNN 自动学到的中间层特征是极其强大的视觉表示。',
      tags: ['CV', 'ImageNet'],
    },
    {
      date: '2013',
      title: 'Word2Vec — 词的分布式表示',
      desc: 'Mikolov 等人提出 CBOW 和 Skip-gram，将词映射到稠密向量空间。"国王 - 男人 + 女人 ≈ 女王"的类比推理震惊 NLP 界，掀起了分布式表示的研究浪潮。',
      tags: ['NLP', '分布式'],
    },
    {
      date: '2015',
      title: 'ResNet — 残差连接让深层网络可用',
      desc: 'He 等人提出残差学习，解决了深层网络的退化问题。152 层的 ResNet 把 ImageNet 错误率降到 3.57%，其 skip connection 思想影响了后续几乎所有架构设计。',
      tags: ['CV', '架构'],
    },
    {
      date: '2018',
      title: 'BERT — 预训练 + 微调范式',
      desc: 'Devlin 等人提出 BERT，通过掩码语言建模（MLM）在大规模无标注文本上预训练，再在下游任务微调。这一范式迅速统治 NLP，也启发了视觉领域的 MAE 等方法。',
      tags: ['NLP', '预训练'],
    },
    {
      date: '2020',
      title: '对比学习爆发：SimCLR / MoCo v2',
      desc: 'Chen 等人（SimCLR）和 He 等人（MoCo）将对比学习推向自监督视觉的前沿。核心思想简单：同一图片的不同增强在表示空间靠近，不同图片推开。无需负样本的 BYOL 同期出现。',
      tags: ['自监督', 'CV'],
    },
    {
      date: '2021',
      title: 'MAE — 掩码自编码器回归',
      desc: 'He 等人提出 MAE，将 BERT 的掩码思路搬到视觉：遮掉 75% 的 patch，让解码器重建原图。极简的设计、极高的效率，在 ImageNet 上超越对比学习方法。',
      tags: ['自监督', 'CV'],
    },
    {
      date: '2023',
      title: 'DINOv2 — 通用视觉特征',
      desc: 'Meta AI 发布 DINOv2，在 1.42 亿张策划数据集上训练的自蒸馏 ViT。冻结特征可直接用于深度估计、语义分割、图像检索等大量任务，无需微调。标志着通用视觉表示的成熟。',
      tags: ['自监督', '通用'],
    },
  ]
};

/* ===== Markdown 编译内容 ===== */
if (!window.REPLEARNING_CONTENT) {
  throw new Error('表征学习 Markdown 编译内容未加载，请先运行 scripts/build-cards.py');
}
Object.assign(CONTENT, window.REPLEARNING_CONTENT);

/* ─── 学术会议与期刊 ─── */

/* ===== 包装为板块数据（reanotes 多板块架构） ===== */
window.BOARD_DATA = window.BOARD_DATA || {};
(function () {
  var content = Object.assign({}, CONTENT);
  delete content.home;
  BOARD_DATA['replearning'] = {
    home: CONTENT['home'],
    navTree: NAV_TREE,
    content: content,
  };
})();
})();
