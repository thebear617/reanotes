(function () {
/* ===== 首页数据 ===== */
const HOME_GRID = [
  { id: 'f-problem', icon: '🎯', title: '问题定义（科研角度）', desc: 'gap · 重新表述 · 指标本身' },
  { id: 'f-arch',    icon: '🏗️', title: '架构探索',          desc: '新模块 · 消融 · 可解释性' },
  { id: 'f-rep',     icon: '🧩', title: '特征与表示',        desc: '输入表示 · 自监督任务 · 增强' },
  { id: 'f-train',   icon: '🔥', title: '训练方法',          desc: '新损失 · 新优化 · 稳定性根因' },
  { id: 'f-tune',    icon: '🔬', title: '调优与验证',        desc: '消融是灵魂 · 公平对比' },
  { id: 'f-shallow', icon: '🛠️', title: '科研浅尝辄止',      desc: '数据清洗 · 部署 · Pipeline' },
  { id: 'f-vs',      icon: '⚖️', title: '科研 vs 工程',      desc: '为什么好，能否推广' },
];

const HOME_UPDATES = [
  { date: '2026-07-11', text: '新增「深度学习科研」板块：科研主战场与本质', id: 'overview' },
  { date: '2026-07-11', text: '科研主战场：问题定义 · 架构 · 表示 · 训练 · 调优', id: 'f-arch' },
  { date: '2026-07-11', text: '科研 vs 工程：根本区别', id: 'f-vs' },
];

const HOME_QUICKREF = [
  { label: '消融',   slogan: '科研的灵魂：每个组件都必要',  models: 'ablation study' },
  { label: '假设',   slogan: '提假设 → 对照实验 → 验证/证伪', models: 'hypothesis-driven' },
  { label: '推广',   slogan: '结论要能推广，而非只刷分',      models: 'generalization' },
];

/* ===== 导航树 ===== */
const NAV_TREE = [
  { id: 'overview', icon: '🔭', label: '科研视角总览' },
  { type: 'divider' },
  {
    id: 'fronts', icon: '🔬', label: '科研主战场',
    children: [
      { id: 'f-problem', label: '问题定义（角度）' },
      { id: 'f-arch',    label: '架构探索' },
      { id: 'f-rep',     label: '特征与表示' },
      { id: 'f-train',   label: '训练方法' },
      { id: 'f-tune',    label: '调优与验证' },
    ]
  },
  { type: 'divider' },
  { id: 'f-shallow', icon: '🛠️', label: '科研浅尝辄止' },
  { id: 'f-vs',     icon: '⚖️', label: '科研 vs 工程' },
];

/* ===== 内容 ===== */
const CONTENT = {};

CONTENT['home'] = {
  type: 'home',
  title: '深度学习科研 · 研究视角',
  desc: '同一个深度学习流程，科研关注的重心与工程不同：它追问"为什么有效、能否推广"。这里按科研主战场组织，每个环节都回链到「深度学习工程」的对应阶段。',
  gridCards: HOME_GRID,
  recentUpdates: HOME_UPDATES,
  quickRef: HOME_QUICKREF,
};

/* ─── 科研视角总览 ─── */
CONTENT['overview'] = {
  title: '🔭 科研视角总览',
  desc: '工程问"效果好不好"，科研问"为什么好、能否推广"。这一页先把二者的根本区别摆清，再给出科研主战场的入口。',
  cards: [
    {
      icon: '🔑',
      title: '根本区别',
      tags: ['为什么', '好不好'],
      expanded: true,
      body: `<p><strong>工程项目问的是"这样做效果好不好"；</strong></p>
      <p><strong>科研项目问的是"为什么效果好，这个发现能不能推广到其他场景"。</strong></p>
      <p>所以科研在每个环节都会多一层：提假设 → 设计对照实验 → 验证/证伪 → 归纳出可推广的结论。</p>`
    },
    {
      icon: '🗺️',
      title: '科研主战场一览',
      tags: ['发力点'],
      body: `<ul>
        <li><a href="#dlresearch/f-problem">问题定义（角度不同）</a>：gap 在哪、能否重新表述、指标本身合理吗</li>
        <li><a href="#dlresearch/f-arch">架构探索</a>：设计新模块、消融搞清为什么有效、可解释性</li>
        <li><a href="#dlresearch/f-rep">特征与表示</a>：更好的输入表示、自监督/预训练任务、数据增强创新</li>
        <li><a href="#dlresearch/f-train">训练方法</a>：新损失函数、新优化策略、训练稳定性根因</li>
        <li><a href="#dlresearch/f-tune">调优与验证</a>：消融是灵魂、公平对比、多数据集多 seed</li>
      </ul>
      <p>每个主战场都回链到 <a href="#dlproject">深度学习工程</a> 的对应阶段，方便对照"科研打法"和"工程做法"。</p>`
    },
    {
      icon: '📖',
      title: '怎么读这个板块',
      tags: ['使用'],
      body: `<p>· 想看某环节的科研打法 → 左侧「科研主战场」逐级展开。<br>
      · 想看同一环节工程怎么做 → 切到 <a href="#dlproject">深度学习工程</a>。<br>
      · 想一眼看清二者本质差异 → 看 <a href="#dlresearch/f-vs">科研 vs 工程</a>。</p>`
    }
  ]
};

/* ─── 问题定义（科研角度） ─── */
CONTENT['f-problem'] = {
  title: '🎯 问题定义（科研角度）',
  desc: '工程关心指标是否满足业务需求；科研在问题定义上多一层"值不值得研究"的审视。',
  cards: [
    {
      icon: '🕳️',
      title: '这个 gap 存在吗？',
      tags: ['定位'],
      body: `<p>这个问题有没有被很好地解决过？<strong>真正的 gap 在哪</strong>？科研的价值往往在于找准一个尚未被满足、且有意义的问题，而不是在已被解决的方向上堆技巧。</p>`
    },
    {
      icon: '♻️',
      title: '能不能重新表述',
      tags: ['通用性'],
      body: `<p>能不能把问题<strong>重新表述得更通用、更有理论意义</strong>？一个更通用的提法，往往能引出更本质的贡献，也更容易推广。</p>`
    },
    {
      icon: '📏',
      title: '指标本身合理吗',
      tags: ['元贡献'],
      body: `<p>评估指标本身合不合理？很多科研工作会先指出"<strong>现有指标测不出真正的问题</strong>"——这本身就是一项贡献，因为它重新定义了什么是"好"。</p>`
    },
    {
      icon: '🔗',
      title: '回链',
      tags: ['工程'],
      body: `<p>工程视角下的问题定义见 <a href="#dlproject/p1">深度学习工程 · 问题定义</a>：任务类型、评估指标选择、可行性评估。</p>`
    }
  ]
};

/* ─── 架构探索 ─── */
CONTENT['f-arch'] = {
  title: '🏗️ 架构探索',
  desc: '科研在工程"选个架构"之上，把架构本身当成研究对象——这是科研的重头戏。',
  cards: [
    {
      icon: '🧩',
      title: '设计新模块 / 层',
      tags: ['创新'],
      body: `<p>设计新的模块或层：attention 变体、新的归一化方式、新的连接方式等。目标是带来可解释、可迁移的结构性改进，而非单纯堆叠深度。</p>`
    },
    {
      icon: '🔬',
      title: '消融搞清"为什么有效"',
      tags: ['机制'],
      body: `<p>做架构的消融实验，搞清楚"<strong>为什么这个改动有效</strong>"，而不只是"它有效"。科研拒绝把成功当黑箱。</p>`
    },
    {
      icon: '💡',
      title: '从假设到验证',
      tags: ['方法论'],
      body: `<p>从直觉或理论出发<strong>提假设，再用实验验证</strong>，而不是纯粹试错。先有机制解释，再有结构创新，形成闭环。</p>`
    },
    {
      icon: '🔎',
      title: '可解释性',
      tags: ['机制'],
      body: `<p>关注<strong>可解释性</strong>：这个架构改进的内在机制是什么？能讲清楚"为什么"，贡献才立得住、才推得广。</p>`
    },
    {
      icon: '🔗',
      title: '回链',
      tags: ['工程'],
      body: `<p>工程视角下的模型设计见 <a href="#dlproject/p4">深度学习工程 · 模型设计</a>：baseline 起步、架构选择、损失函数。</p>`
    }
  ]
};

/* ─── 特征与表示 ─── */
CONTENT['f-rep'] = {
  title: '🧩 特征与表示',
  desc: '特征/表示常常是研究创新点所在——尤其当"如何表示数据"本身就值得深挖。',
  cards: [
    {
      icon: '🎨',
      title: '更好的输入表示',
      tags: ['表示'],
      body: `<p>如何设计更好的输入表示：embedding 方式、多模态融合方式等。表示的优劣直接决定上游模型的天花板。</p>`
    },
    {
      icon: '🔄',
      title: '自监督 / 预训练任务设计',
      tags: ['大方向'],
      body: `<p>自监督 / 预训练任务的设计<strong>本身就是一个很大的研究方向</strong>。设计一个好的 pretext task，往往比换骨干网络带来更本质的提升。</p>`
    },
    {
      icon: '✨',
      title: '数据增强创新',
      tags: ['针对性'],
      body: `<p>数据增强策略的创新，尤其是<strong>针对特定任务设计的增强方法</strong>。好的增强等于注入更强的先验，常是论文的关键 trick。</p>`
    },
    {
      icon: '🔗',
      title: '回链',
      tags: ['工程'],
      body: `<p>工程视角下的特征工程见 <a href="#dlproject/p3">深度学习工程 · 特征工程</a>：归一化、增强、Tokenization、Pipeline。</p>`
    }
  ]
};

/* ─── 训练方法 ─── */
CONTENT['f-train'] = {
  title: '🔥 训练方法',
  desc: '科研在训练环节关注的不是"调出好结果"，而是"为什么这样训练有效"。',
  cards: [
    {
      icon: '🎯',
      title: '新的损失函数设计',
      tags: ['目标'],
      body: `<p>新的损失函数设计——<strong>不只是调权重，而是重新设计目标函数的形式</strong>。目标函数定义了模型在优化什么，改目标往往改命运。</p>`
    },
    {
      icon: '🧪',
      title: '新的优化策略',
      tags: ['范式'],
      body: `<p>新的优化策略：课程学习、对比学习、蒸馏等<strong>训练范式</strong>。它们改变的是"怎么学"，而不只是"学什么"。</p>`
    },
    {
      icon: '🩺',
      title: '训练稳定性根因',
      tags: ['诊断'],
      body: `<p>训练稳定性问题的<strong>根因分析</strong>：比如为什么某类模型训练不稳定，提出理论解释 + 解决方案。从现象到根因，是科研的典型路径。</p>`
    },
    {
      icon: '🔗',
      title: '回链',
      tags: ['工程'],
      body: `<p>工程视角下的训练见 <a href="#dlproject/p5">深度学习工程 · 训练</a>：超参、训练循环、早停、实验追踪。</p>`
    }
  ]
};

/* ─── 调优与验证 ─── */
CONTENT['f-tune'] = {
  title: '🔬 调优与验证',
  desc: '科研也调参，但目的不是"刷分"，而是验证假设是否成立。',
  cards: [
    {
      icon: '🔬',
      title: '消融是灵魂',
      tags: ['必要性'],
      body: `<p>消融实验（ablation）是科研的灵魂：证明<strong>每个组件都是必要的</strong>，且改进来自于你说的原因，而不是别的巧合因素。</p>`
    },
    {
      icon: '⚖️',
      title: '公平对比',
      tags: ['可信度'],
      body: `<p>对比实验要公平：<strong>同样的算力、同样的数据、同样的调参努力</strong>，否则结论不可信。科研的诚实比好看的数字更重要。</p>`
    },
    {
      icon: '🌐',
      title: '多数据集 / 多 seed',
      tags: ['非偶然'],
      body: `<p>需要在<strong>多个数据集、多个 seed</strong> 上验证，证明结果不是偶然。一次跑赢可能是运气，多次稳定才站得住。</p>`
    },
    {
      icon: '🔗',
      title: '回链',
      tags: ['工程'],
      body: `<p>工程视角下的调优见 <a href="#dlproject/p6">深度学习工程 · 调优</a>：超参搜索、错误分析、正则化。</p>`
    }
  ]
};

/* ─── 科研浅尝辄止 ─── */
CONTENT['f-shallow'] = {
  title: '🛠️ 科研浅尝辄止的部分',
  desc: '有些环节科研通常不下深功夫——除非那个环节本身就是研究方向。',
  cards: [
    {
      icon: '🧹',
      title: '数据收集 / 清洗的工程细节',
      tags: ['除非数据是贡献'],
      body: `<p>数据收集 / 清洗的工程细节，科研通常浅尝辄止——<strong>除非数据本身就是贡献</strong>（如构建新数据集、新 benchmark）。</p>`
    },
    {
      icon: '📦',
      title: '部署、压缩、上线监控',
      tags: ['除非方向就是压缩'],
      body: `<p>部署、压缩、上线监控，科研一般不深入——<strong>除非研究方向就是模型压缩 / 边缘部署本身</strong>。否则这些是工程的活。</p>`
    },
    {
      icon: '⚙️',
      title: 'Pipeline 工程化',
      tags: ['工程范畴'],
      body: `<p>Pipeline 工程化（如生产级 DataLoader、分布式训练框架）属于工程范畴。科研更关心方法本身，工程关心方法能否稳定、可复现地跑起来。</p>`
    }
  ]
};

/* ─── 科研 vs 工程 ─── */
CONTENT['f-vs'] = {
  title: '⚖️ 科研 vs 工程',
  desc: '一句话收束：工程回答"好不好"，科研回答"为什么好、能否推广"。',
  cards: [
    {
      icon: '🛠️',
      title: '工程：效果好不好',
      tags: ['交付'],
      expanded: true,
      body: `<p>工程项目问的是"<strong>这样做效果好不好</strong>"——能不能满足业务指标、能不能上线、成本能不能接受。以交付和可用为终点。</p>`
    },
    {
      icon: '🔬',
      title: '科研：为什么好，能否推广',
      tags: ['洞察'],
      body: `<p>科研项目问的是"<strong>为什么效果好，这个发现能不能推广到其他场景</strong>"。以可推广的机制性结论为终点，而不是单次跑赢。</p>`
    },
    {
      icon: '🔁',
      title: '一个闭环的差异',
      tags: ['方法论'],
      body: `<p>在每个环节，科研都比工程多一层：<strong>提假设 → 设计对照实验 → 验证/证伪 → 归纳出可推广的结论</strong>。这正是科研与工程最本质的分野。</p>`
    }
  ]
};

/* ===== 包装为板块数据（reanotes 多板块架构） ===== */
window.BOARD_DATA = window.BOARD_DATA || {};
(function () {
  var content = Object.assign({}, CONTENT);
  delete content.home;
  BOARD_DATA['dlresearch'] = {
    home: CONTENT['home'],
    navTree: NAV_TREE,
    content: content,
  };
})();
})();
