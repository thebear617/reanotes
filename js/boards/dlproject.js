(function () {
/* ===== 首页数据 ===== */
const HOME_GRID = [
  { id: 'p1',     icon: '①', title: '问题定义',   desc: '任务类型 · 评估指标 · 可行性' },
  { id: 'p2',     icon: '②', title: '数据准备',   desc: '收集标注 · 清洗 · EDA · 划分' },
  { id: 'p3',     icon: '③', title: '特征工程',   desc: '归一化 · 增强 · Tokenization · Pipeline' },
  { id: 'p4',     icon: '④', title: '模型设计',   desc: 'baseline · 架构 · 损失函数' },
  { id: 'p5',     icon: '⑤', title: '训练',       desc: '超参 · 循环 · 早停 · 实验追踪' },
  { id: 'p6',     icon: '⑥', title: '调优',       desc: '超参搜索 · 错误分析 · 正则化' },
  { id: 'p7',     icon: '⑦', title: '评估',       desc: '测试纪律 · 消融 · 鲁棒性' },
  { id: 'p8',     icon: '⑧', title: '部署监控',   desc: '量化 · API · 漂移 · 反馈闭环' },
];

const HOME_UPDATES = [
  { date: '2026-07-11', text: '新增「深度学习工程」板块：八阶段流程', id: 'overview' },
  { date: '2026-07-11', text: '八阶段：问题定义 → 部署监控', id: 'p1' },
  { date: '2026-07-11', text: '科研视角拆分至独立板块「深度学习科研」', id: 'overview' },
];

const HOME_QUICKREF = [
  { label: '指标',   slogan: '指标选错，后面全白搭',      models: 'accuracy / F1 / mAP / BLEU' },
  { label: '测试集', slogan: '测试集不能用来调参',          models: 'hold-out 纪律' },
  { label: '消融',   slogan: '科研的灵魂：每个组件都必要',  models: 'ablation study' },
];

/* ===== 导航树 ===== */
const NAV_TREE = [
  { id: 'overview', icon: '🗺️', label: '流程全景' },
  { type: 'divider' },
  {
    id: 'stages', icon: '🔢', label: '全流程八阶段',
    children: [
      { id: 'p1', label: '1 问题定义' },
      { id: 'p2', label: '2 数据准备' },
      { id: 'p3', label: '3 特征工程' },
      { id: 'p4', label: '4 模型设计' },
      { id: 'p5', label: '5 训练' },
      { id: 'p6', label: '6 调优' },
      { id: 'p7', label: '7 评估' },
      { id: 'p8', label: '8 部署监控' },
    ]
  },
  { type: 'divider' },
];

/* ===== 内容 ===== */
const CONTENT = {};

CONTENT['home'] = {
  type: 'home',
  title: '深度学习工程 · 项目全流程',
  desc: '从问题定义到部署监控的完整深度学习项目流程地图。横切视角：一个项目怎么做；与「表征学习」纵切某一环节互为补充。',
  gridCards: HOME_GRID,
  recentUpdates: HOME_UPDATES,
  quickRef: HOME_QUICKREF,
};

/* ─── 流程全景 ─── */
CONTENT['overview'] = {
  title: '🗺️ 流程全景',
  desc: '一个深度学习项目从想法到上线，通常串起下面八个阶段。任意一阶段出问题都会向上游传导，所以顺序理解比单点深入更重要。',
  cards: [
    {
      icon: '🔢',
      title: '八阶段一览',
      tags: ['全局'],
      expanded: true,
      body: `<ol class="flow-list">
        <li><strong>问题定义</strong> — 任务类型、评估指标、可行性</li>
        <li><strong>数据准备</strong> — 收集标注、清洗、EDA、划分</li>
        <li><strong>特征工程与预处理</strong> — 归一化、增强、Tokenization、Pipeline</li>
        <li><strong>模型设计与选型</strong> — baseline、架构、损失函数</li>
        <li><strong>训练</strong> — 超参、训练循环、早停、实验追踪</li>
        <li><strong>调优</strong> — 超参搜索、错误分析、正则化</li>
        <li><strong>评估</strong> — 测试纪律、消融、鲁棒性与公平性</li>
        <li><strong>部署与监控</strong> — 量化、API、漂移监控、反馈闭环</li>
      </ol>
      <p>每个阶段点开左侧「全流程八阶段」即可查看该环节的要点。</p>`
    },
    {
      icon: '🧩',
      title: '两个视角：纵切 vs 横切',
      tags: ['定位'],
      body: `<p>本板块是<strong>横切</strong>：沿时间轴把一个项目从头到尾讲一遍。</p>
      <p>而「<a href="#replearning">表征学习</a>」是<strong>纵切</strong>：单挑「特征/表示」这一环节往深处钻。</p>
      <p>两者互补——横切告诉你"这一步在哪、为什么在这"，纵切告诉你"这一步怎么做才算好"。</p>`
    },
    {
      icon: '📖',
      title: '怎么读这个板块',
      tags: ['使用'],
      body: `<p>· 想快速建立全局观 → 看这一页和首页流程卡。<br>
      · 想深入某环节 → 左侧「全流程八阶段」逐级展开。<br>
      · 想从科研视角看每个环节怎么打 → 看 <a href="#dlresearch">深度学习科研</a>。</p>`
    }
  ]
};

/* ─── 1 问题定义 ─── */
CONTENT['p1'] = {
  title: '① 问题定义',
  desc: '最容易被跳过的阶段，却决定后面所有努力的方向。指标选错，后面全白搭。',
  cards: [
    {
      icon: '🎯',
      title: '明确任务类型',
      tags: ['分类', '回归', '检测', '生成'],
      body: `<p>先认清这是<strong>分类</strong>（给标签）、<strong>回归</strong>（给数值）、<strong>检测</strong>（框+类）还是<strong>生成</strong>（造样本）。任务类型直接决定输出层、损失函数和评价指标。</p>`
    },
    {
      icon: '📏',
      title: '确定评估指标',
      tags: ['指标'],
      body: `<p>accuracy / F1 / mAP / BLEU 等，<strong>这一步很关键，指标选错后面全白搭</strong>。指标要能真实反映业务目标，而不是只挑一个好看的。</p>`
    },
    {
      icon: '💡',
      title: '评估可行性',
      tags: ['数据', '算力', '周期'],
      body: `<p>诚实地问三个问题：数据<strong>能不能拿到</strong>？算力<strong>预算</strong>够不够？时间<strong>周期</strong>赶不赶得上？不可行的方案尽早回头，比闷头做三个月再推翻划算。</p>`
    }
  ]
};

/* ─── 2 数据准备 ─── */
CONTENT['p2'] = {
  title: '② 数据准备',
  desc: '深度学习里最"脏活"也最容易被低估的阶段。数据质量决定上限，模型只是逼近它。',
  cards: [
    {
      icon: '📥',
      title: '收集 / 爬取 / 标注',
      tags: ['数据'],
      body: `<p>从源头拿数据：公开数据集、业务日志、爬虫，或人工标注。标注规范要先统一，否则噪声会一路传到模型里。</p>`
    },
    {
      icon: '🧹',
      title: '数据清洗',
      tags: ['去重', '去噪', '缺失值'],
      body: `<p>去重、去噪、处理缺失值。重复样本会偷偷抬高评测分数；噪声标签是模型学偏的常见根因。</p>`
    },
    {
      icon: '🔍',
      title: '探索性分析（EDA）',
      tags: ['分布', '异常值', '均衡'],
      body: `<p>看分布、看异常值、看类别是否均衡。类别严重不均衡时，准确率会骗人，需要换指标或重采样。</p>`
    },
    {
      icon: '✂️',
      title: '划分 train / val / test',
      tags: ['防泄露'],
      body: `<p>切分时要注意<strong>避免数据泄露</strong>：比如<strong>时间序列不能随机划分</strong>，否则未来信息泄漏进训练，线下好看线上翻车。</p>`
    }
  ]
};

/* ─── 3 特征工程与预处理 ─── */
CONTENT['p3'] = {
  title: '③ 特征工程与预处理',
  desc: '把原始数据整理成模型能吃、且容易学的形式。',
  cards: [
    {
      icon: '📐',
      title: '归一化 / 标准化',
      tags: ['缩放'],
      body: `<p>把数值拉到相近尺度，让梯度下降更稳更快。不同特征量纲差太多时尤其必要。</p>`
    },
    {
      icon: '🎨',
      title: '数据增强',
      tags: ['图像', '文本', '音频'],
      body: `<p>图像的翻转裁剪、文本的同义替换、音频的变速变调等。本质是用先验<strong>人造更多样本</strong>，缓解过拟合、提升泛化。</p>`
    },
    {
      icon: '🔤',
      title: 'Tokenization',
      tags: ['NLP'],
      body: `<p>如果是 NLP，先把文本切成 token 并映射到 id。分词粒度（字/词/子词）会影响语义保留和词表大小。</p>`
    },
    {
      icon: '⚙️',
      title: '构建 DataLoader / Pipeline',
      tags: ['工程'],
      body: `<p>把上面的步骤串成可复用的数据管道，支持批量、打乱、并行读取。Pipeline 的稳定性属于工程范畴，但直接影响训练可复现。</p>`
    }
  ]
};

/* ─── 4 模型设计与选型 ─── */
CONTENT['p4'] = {
  title: '④ 模型设计与选型',
  desc: '从简单 baseline 起步，再决定要不要上复杂架构。',
  cards: [
    {
      icon: '🪜',
      title: '从简单 baseline 起步',
      tags: ['baseline'],
      body: `<p><strong>不要一上来就上最复杂的模型</strong>。先跑通一个简单基线，它既是下限参照，也能帮你快速定位问题出在数据还是模型。</p>`
    },
    {
      icon: '🏗️',
      title: '选择架构',
      tags: ['CNN', 'Transformer', 'RNN'],
      body: `<p>CNN、Transformer、RNN 等，或考虑<strong>预训练模型微调</strong>。选型要看数据形态（图像/序列/图）和任务，而不是哪个火用哪个。</p>`
    },
    {
      icon: '🎯',
      title: '确定损失函数',
      tags: ['目标'],
      body: `<p>损失函数定义了"模型在优化什么"。分类用交叉熵，回归用 MSE，但科研常会重新设计目标函数的形式本身。</p>`
    }
  ]
};

/* ─── 5 训练 ─── */
CONTENT['p5'] = {
  title: '⑤ 训练',
  desc: '把数据喂进去，让模型在损失引导下更新参数。',
  cards: [
    {
      icon: '🎛️',
      title: '设置超参数',
      tags: ['学习率', 'batch', '优化器'],
      body: `<p>学习率、batch size、优化器（SGD/Adam 等）。学习率通常是影响最大也最该先调的那个。</p>`
    },
    {
      icon: '🔁',
      title: '训练循环与监控',
      tags: ['loss'],
      body: `<p>搭建训练循环，<strong>监控 loss 曲线</strong>。loss 不降可能是学习率、数据或梯度的问题，曲线形状本身就是诊断工具。</p>`
    },
    {
      icon: '⏱️',
      title: '早停（early stopping）',
      tags: ['防过拟合'],
      body: `<p>在验证集上监控，当指标不再提升就停下，防止在训练集上过拟合。记得保存"最佳"那一份，不是最后一份。</p>`
    },
    {
      icon: '📊',
      title: '实验追踪',
      tags: ['wandb', 'tensorboard'],
      body: `<p>推荐用 wandb / tensorboard 之类的工具做实验追踪，把超参、指标、产物都记下来。<strong>可复现</strong>是科研和工程共同的底线。</p>`
    }
  ]
};

/* ─── 6 调优 ─── */
CONTENT['p6'] = {
  title: '⑥ 调优',
  desc: '在 baseline 之上把性能推到该有的位置。',
  cards: [
    {
      icon: '🔧',
      title: '超参数搜索',
      tags: ['网格', '随机', '贝叶斯'],
      body: `<p>网格搜索、随机搜索、贝叶斯优化。搜索空间比搜索算法往往更影响结果——先想清楚哪些超参真的重要。</p>`
    },
    {
      icon: '🐞',
      title: '错误分析',
      tags: ['针对性改进'],
      body: `<p>看模型在<strong>哪些样本上表现差</strong>，把失败样本聚类，针对性改进。这比盲调超参高效得多，也是发现数据问题的入口。</p>`
    },
    {
      icon: '🛡️',
      title: '正则化',
      tags: ['dropout', 'weight decay'],
      body: `<p>dropout、weight decay、数据增强等手段控制复杂度，抑制过拟合。加正则要配合验证集观察，过强会欠拟合。</p>`
    }
  ]
};

/* ─── 7 评估 ─── */
CONTENT['p7'] = {
  title: '⑦ 评估',
  desc: '在没被调过参的数据上，诚实地给模型下结论。',
  cards: [
    {
      icon: '🚫',
      title: '测试集纪律',
      tags: ['hold-out'],
      body: `<p>在测试集上做最终评估，<strong>确保没有用测试集调过参</strong>。一旦拿测试集做选择，它就不再是"未见数据"，分数会虚高。</p>`
    },
    {
      icon: '🔬',
      title: '消融实验（ablation）',
      tags: ['贡献归因'],
      body: `<p>做消融实验，搞清楚<strong>哪些设计真正起作用</strong>。逐个去掉组件看指标掉多少，才能区分"真有效"和"凑热闹"。</p>`
    },
    {
      icon: '⚖️',
      title: '鲁棒性与公平性',
      tags: ['偏见', '边缘 case'],
      body: `<p>检查模型的鲁棒性和公平性：有没有偏见、边缘 case（长尾/对抗样本）表现如何。这往往是模型能不能上真场景的分水岭。</p>`
    }
  ]
};

/* ─── 8 部署与监控 ─── */
CONTENT['p8'] = {
  title: '⑧ 部署监控',
  desc: '模型价值真正兑现的地方，却常被忽略。',
  cards: [
    {
      icon: '🗜️',
      title: '压缩 / 量化',
      tags: ['边缘设备'],
      body: `<p>如果要上线到<strong>资源受限设备</strong>，做模型压缩/量化（如 INT8），在可接受精度损失内换延迟和体积。</p>`
    },
    {
      icon: '🚀',
      title: '部署为 API / 集成产品',
      tags: ['上线'],
      body: `<p>把模型部署为 API 或集成到产品里。这里大量是工程：服务化、批处理、限流、降级，和训练是两套技术栈。</p>`
    },
    {
      icon: '📉',
      title: '监控漂移',
      tags: ['data drift', 'concept drift'],
      body: `<p>上线后持续监控性能漂移：<strong>data drift</strong>（输入分布变）和 <strong>concept drift</strong>（规律变）。漂移不处理，模型会静默退化。</p>`
    },
    {
      icon: '🔄',
      title: '反馈闭环',
      tags: ['迭代'],
      body: `<p>建立反馈闭环，收集新数据（尤其是失败样本）用于下一轮迭代。部署不是终点，是下一轮数据准备的起点。</p>`
    }
  ]
};

/* ===== 包装为板块数据（reanotes 多板块架构） ===== */
window.BOARD_DATA = window.BOARD_DATA || {};
(function () {
  var content = Object.assign({}, CONTENT);
  delete content.home;
  BOARD_DATA['dlproject'] = {
    home: CONTENT['home'],
    navTree: NAV_TREE,
    content: content,
  };
})();
})();
