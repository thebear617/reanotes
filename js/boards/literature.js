(function () {
/* ===== 首页数据 ===== */
const HOME_GRID = [
  { id: 'literature', icon: '📚', title: '文献索引',       desc: '主线综述与阅读顺序' },
  { id: 'venues',     icon: '🎓', title: '学术会议与期刊', desc: '顶会 / 期刊官方导航' },
];

/* ===== 导航树 ===== */
const NAV_TREE = [
  { id: 'literature', icon: '📚', label: '文献索引' },
  { id: 'venues',     icon: '🎓', label: '学术会议与期刊' },
];

/* ===== 内容 ===== */
const CONTENT = {};

CONTENT['home'] = {
  type: 'home',
  title: '文献索引',
  desc: '跨领域的学术论文索引与会议期刊导航。点击左侧导航或下方卡片开始浏览。',
  gridCards: HOME_GRID,
};

/* ─── 文献索引（表格形式） ─── */
CONTENT['literature'] = {
  title: '📚 文献索引',
  litTable: {
    columns: [
      { key: 'name',        label: '文献名',     type: 'link' },
      { key: 'date',        label: '发表日期',   type: 'text' },
      { key: 'venue',       label: '会刊',        type: 'text' },
      { key: 'domain',      label: '领域',       type: 'domain' },
      { key: 'tags',        label: '标签',       type: 'tags' },
      { key: 'status',      label: '文献状态',   type: 'status' },
      { key: 'focus',       label: '建议重点读', type: 'text' },
    ],
    rows: [
      {
        name: 'Attention Is All You Need',
        url: 'https://arxiv.org/abs/1706.03762',
        date: '2017-06',
        venue: 'NeurIPS 2017',
        domain: 'NLP·Transformer', dkind: 'nlp',
        tags: ['经典', '必读'],
        status: '已读', statusKind: 'deep',
        focus: 'Transformer 原始论文，NLP 领域的划时代之作。'
      },
      {
        name: 'Representation Learning: A Review and New Perspectives',
        url: 'https://arxiv.org/abs/1206.5538',
        date: '2012-06',
        venue: 'TPAMI 2014',
        domain: '表征学习', dkind: 'general',
        tags: ['经典', '必读打底'],
        status: '未读', statusKind: 'unread',
        focus: '重点读 Introduction、"What makes a representation good?"、总结与开放问题；中间大量早期模型细节可先跳过。'
      },
      {
        name: 'Self-supervised Learning: Generative or Contrastive',
        url: 'https://arxiv.org/abs/2006.08218',
        date: '2020-06',
        venue: 'arXiv 预印本',
        domain: '自监督（CV·NLP·图）', dkind: 'ssl',
        tags: ['入门地图'],
        status: '未读', statusKind: 'unread',
        focus: '作为入门地图，不要当成最终目录；BYOL / VICReg / 掩码潜空间预测等后来方法放进去会有边界问题。'
      },
      {
        name: 'A Cookbook of Self-Supervised Learning',
        url: 'https://arxiv.org/abs/2304.12210',
        date: '2023-04',
        venue: 'arXiv 预印本',
        domain: '自监督（通用）', dkind: 'ssl',
        tags: ['工具书', 'LeCun 组'],
        status: '未读', statusKind: 'unread',
        focus: '不建议从头逐字读。先看目录、导论和总结，把它当作工具书查。'
      },
      {
        name: 'A Survey on Self-Supervised Representation Learning',
        url: 'https://arxiv.org/abs/2308.11455',
        date: '2023-08',
        venue: 'arXiv 预印本',
        domain: '视觉自监督（CV）', dkind: 'cv',
        tags: ['细分类', '视觉'],
        status: '未读', statusKind: 'unread',
        focus: '偏视觉自监督，不要把它当成所有表征学习的总分类；想看清楚现代方法分类时再读。'
      },
    ]
  }
};

/* ─── 学术会议与期刊 ─── */
CONTENT['venues'] = {
  title: '🎓 学术会议与期刊',
  desc: '机器学习 / 深度学习方向主要的顶会顶刊。点击卡片直接跳转官方页面（新标签页打开）。',
  linkSections: [
    {
      title: '顶级会议',
      items: [
        { name: 'NeurIPS', field: 'ML·多模态', kind: 'ml', desc: 'Conference on Neural Information Processing Systems', note: '表征学习 / 自监督学习论文的重镇；多模态表征学习常见于此', url: 'https://neurips.cc/' },
        { name: 'ICML', field: 'ML', kind: 'ml', desc: 'International Conference on Machine Learning', note: '机器学习综合顶会，表征学习论文数量大', url: 'https://icml.cc/' },
        { name: 'ICLR', field: '表征学习', kind: 'ml', desc: 'International Conference on Learning Representations', note: '名字直接带 Representations，表征学习论文最集中的会议之一', url: 'https://iclr.cc/' },
        { name: 'CVPR', field: 'CV', kind: 'cv', desc: 'Conference on Computer Vision and Pattern Recognition', note: '表征学习聚焦视觉领域的主场（对比学习、自监督视觉预训练）', url: 'https://cvpr.thecvf.com/' },
        { name: 'ICCV', field: 'CV', kind: 'cv', desc: 'International Conference on Computer Vision', note: '视觉领域顶会，自监督视觉预训练论文集中', url: 'https://iccv.thecvf.com/' },
        { name: 'ECCV', field: 'CV', kind: 'cv', desc: 'European Conference on Computer Vision', note: '视觉领域顶会（欧洲分会）', url: 'https://eccv.ecva.net/' },
        { name: 'ACL', field: 'NLP', kind: 'nlp', desc: 'Association for Computational Linguistics', note: 'NLP 表征学习（词向量、句子表征、预训练语言模型）主场', url: 'https://www.aclweb.org/' },
        { name: 'EMNLP', field: 'NLP', kind: 'nlp', desc: 'Conference on Empirical Methods in Natural Language Processing', note: 'NLP 实证方法顶会，预训练语言模型论文密集', url: 'https://2026.emnlp.org/' },
        { name: 'NAACL', field: 'NLP', kind: 'nlp', desc: 'North American Chapter of the ACL', note: 'ACL 北美分会，NLP 表征学习论文集中', url: 'https://naacl.org/' },
        { name: 'AAAI', field: 'AI', kind: 'ai', desc: 'Association for the Advancement of Artificial Intelligence', note: '综合性人工智能顶会', url: 'https://aaai.org/conference/aaai/' },
        { name: 'KDD', field: '图·数据', kind: 'graph', desc: 'Knowledge Discovery and Data Mining', note: '偏应用 / 数据挖掘；图表征学习常见于此', url: 'https://kdd.org/' },
      ]
    },
    {
      title: '顶级期刊',
      items: [
        { name: 'JMLR', field: 'ML', kind: 'ml', desc: 'Journal of Machine Learning Research', note: '机器学习权威开源期刊', url: 'https://www.jmlr.org/' },
        { name: 'TPAMI', field: 'CV', kind: 'cv', desc: 'IEEE Transactions on Pattern Analysis and Machine Intelligence', note: '视觉 / 表征学习方向权威期刊', url: 'https://www.computer.org/csdl/journal/tp' },
        { name: 'Nature Machine Intelligence', field: 'ML', kind: 'ml', desc: 'Nature 旗下 AI 期刊', note: '近年影响力上升较快', url: 'https://www.nature.com/natmachintell/' },
        { name: 'Machine Learning', field: 'ML', kind: 'ml', desc: 'Springer 机器学习期刊', note: '表征学习相关论文常见于老牌 ML 期刊', url: 'https://link.springer.com/journal/10994' },
      ]
    },
    {
      title: 'Awesome 合集',
      items: [
        { name: 'papers.cool', field: '论文', kind: 'general', desc: 'AI 论文合集浏览站点', note: '按会议/年份浏览，支持关键词搜索和 PDF 下载', url: 'https://papers.cool/' },
      ]
    },
  ]
};

/* ===== 注册 ===== */
window.BOARD_DATA = window.BOARD_DATA || {};
(function () {
  var content = Object.assign({}, CONTENT);
  delete content.home;
  BOARD_DATA['literature'] = {
    home: CONTENT['home'],
    navTree: NAV_TREE,
    content: content,
  };
})();
})();
