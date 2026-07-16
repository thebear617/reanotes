/* ===== 表征学习 · 卡片数据 =====
 * 由 scripts/build-cards.py 从 content/replearning/**.md 自动生成。
 * 请勿手改本文件；改 content/ 下的 .md 后重跑 build-cards.py。
 */
window.REPLEARNING_CARDS = {
  "architecture": [
    {
      "icon": "🔗",
      "title": "完整的归属链",
      "tags": [
        "分类"
      ],
      "expanded": false,
      "body": "<p><strong>自编码器</strong></p>\n<ul class=\"nested-list\"><li>架构上 → 编码器-解码器架构</li><li>任务上 → 表示学习 / 重构范式</li><li>设计上 → 信息压缩范式（Compression via Bottleneck）</li><li>学习上 → 自监督学习</li></ul>\n<p><strong>U-Net</strong></p>\n<ul class=\"nested-list\"><li>架构上 → 编码器-解码器架构</li><li>任务上 → 密集预测范式（Dense Prediction）</li><li>设计上 → 上下文+定位范式（Context + Localization via Skip Connections）</li><li>学习上 → 监督学习</li></ul>\n<p>它们共享一个父亲（编码器-解码器），但母亲（任务目标）完全不同——就像螺丝刀和开瓶器，都是\"手持工具\"，但设计语言截然不同。</p>"
    },
    {
      "icon": "🎯",
      "title": "核心对照：跳跃连接（Skip Connection）",
      "tags": [
        "关键差异"
      ],
      "expanded": false,
      "body": "<p><strong>U-Net 不是自编码器——根本原因就在于跳跃连接。</strong></p>\n<ul class=\"nested-list\"><li>自编码器的灵魂：信息必须经过瓶颈压缩——网络被迫<strong>舍弃冗余、提取精华</strong></li><li>U-Net 的设计：跳过瓶颈，编码器每一层的特征图直接拼到解码器对应层——信息有\"高速公路\"</li><li>解码器说：\"底层特征不用你重新生成，我直接给你传上来\"</li></ul>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 一个形象的比喻</div><p><strong>自编码器</strong>：把一本书读一遍，合上书本，凭理解默写出来——中间不能翻书</p></div>\n<p>当有人在 U-Net 中压缩/移除跳连让它更接近自编码器时，分割精度下降，但瓶颈层学会了更有语义意义的表示——这是一个此消彼长的 trade-off。</p>"
    },
    {
      "icon": "🏛️",
      "title": "编码器-解码器家族树",
      "tags": [
        "总览"
      ],
      "expanded": true,
      "body": "<p>所有\"编码器→中间层→解码器\"结构的模型可以划分为两大流派：</p>\n<table class=\"comp-table\"><tr><th></th><th>自编码器（AE）</th><th>密集预测架构（U-Net）</th></tr><tr><td>信息通道</td><td>只能走瓶颈（bottleneck）</td><td>瓶颈 + 跳接连路（skip connection）</td></tr><tr><td>核心机制</td><td>信息压缩 → 迫使学到本质表示</td><td>上下文+定位 → 像素级对齐</td></tr><tr><td>学习方式</td><td>自监督（重构自身）</td><td>监督（逐像素预测）</td></tr><tr><td>学什么</td><td>语义表示 / 紧凑编码</td><td>空间对应关系</td></tr><tr><td>最怕什么</td><td>网络\"作弊\"不走瓶颈</td><td>空间细节在下采样中丢失</td></tr><tr><td>代表</td><td>AE, VAE, MAE, DAE</td><td>U-Net, U-Net++, Attention U-Net</td></tr></table>"
    }
  ],
  "disentangled": [
    {
      "icon": "🔬",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>β-VAE</strong>：在 VAE 的 KL 散度项前加一个权重 β > 1，更强力地约束潜在分布，从而促进解耦</li><li><strong>FactorVAE</strong>：在 β-VAE 基础上加一个判别器，鼓励每个维度独立</li><li><strong>DIP-VAE</strong>：直接约束潜在表示的协方差矩阵</li><li><strong>InfoGAN</strong>：在 GAN 中通过互信息最大化实现解耦</li></ul>"
    },
    {
      "icon": "🧵",
      "title": "解耦的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>解耦（Disentanglement）追求的一种理想状态：</p>\n<ul class=\"nested-list\"><li>改变潜在空间的一个维度 → 输出的<strong>一个</strong>语义属性变化，其他不变</li><li>例如：z₁ 控制旋转、z₂ 控制颜色、z₃ 控制背景——互不干扰</li><li>这使得表示<strong>可解释、可编辑、可组合</strong></li></ul>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 理解要点</div><p>解耦是自编码器\"信息瓶颈\"哲学的极致延伸——既然要把信息压缩到瓶颈，不如强迫每个维度各管一摊。但问题在于：<strong>什么算\"一个语义因子\"？</strong>这本身是主观的。</p></div>"
    }
  ],
  "foundation": [
    {
      "icon": "🧭",
      "title": "表征学习-数学模型和研究目的",
      "tags": [
        "起点"
      ],
      "expanded": true,
      "body": "<h3>一、数学模型</h3>\n<p>可以先把所有模型抽象成：</p>\n<p>$$x \\\\xrightarrow{f_\\\\theta} z \\\\xrightarrow{g_\\\\phi} y$$</p>\n<p>其中：</p>\n<ul class=\"nested-list\"><li>$x$：原始数据，例如图像、文本、语音；</li><li>$f_\\\\theta$：编码器；</li><li>$z$：学习到的特征；</li><li>$g_\\\\phi$：分类头、生成器、检索器或者决策模块；</li><li>$y$：最终输出。</li></ul>\n<p>表征学习真正关心的不是\"用了什么网络\"，而是：保留了输入中的什么信息，舍弃了什么信息，以及这种信息组织方式能否迁移到新的任务。</p>\n<h3>二、研究目的</h3>\n<p>经典的表征学习综述把这个问题描述为：数据背后存在若干解释性变化因素，而不同表示会以不同程度把这些因素纠缠或者分离。</p>\n<p>例如一张猫的照片包含：</p>\n<div class=\"example-box\"><div class=\"example-box-title\">🐱 猫的图片属性示例</div><p>动物类别：猫</p><p>姿态：趴着</p><p>颜色：橘色</p><p>背景：沙发</p><p>光照：较暗</p><p>拍摄角度：侧面</p><p>纹理、像素噪声……</p></div>\n<p>对于猫分类来说，理想表征应该：</p>\n<ul class=\"nested-list\"><li>保留\"猫\"的语义；</li><li>对轻微光照变化保持稳定；</li><li>对背景变化不过度敏感；</li><li>可能保留姿态，但不一定依赖姿态；</li><li>丢弃无意义的传感器噪声。</li></ul>\n<p>但对于姿态估计任务，姿态又必须被保留。</p>\n<p>所以没有脱离任务和环境的\"绝对好表征\"。更准确的问题是：</p>\n<blockquote>对于哪些任务、哪些变化、哪些数据分布，这个表征是好的？</blockquote>"
    }
  ],
  "graph": [
    {
      "icon": "🧩",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>Node2Vec / DeepWalk</strong>：基于随机游走的图嵌入（无监督、浅层）</li><li><strong>GCN（图卷积网络）</strong>：在邻域上做卷积操作，聚合邻居信息</li><li><strong>GAT（图注意力网络）</strong>：用注意力机制动态聚合邻居，自适应权重</li><li><strong>GraphSAGE</strong>：采样邻居 + 聚合，适应大规模图</li><li><strong>图自编码器（GAE / VGAE）</strong>：用自编码器框架重构图结构或节点属性</li></ul>"
    },
    {
      "icon": "🕸️",
      "title": "图表示学习的核心问题",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>图数据有三个核心挑战：</p>\n<ul class=\"nested-list\"><li><strong>非欧空间</strong>：图没有规则的网格结构（不像图像），不能用卷积核直接滑动</li><li><strong>拓扑不变性</strong>：图的排列（permutation）不应该改变表示——需要置换不变性</li><li><strong>多尺度</strong>：节点级、边级、子图级、全图级，每个粒度都需要不同的表示</li></ul>"
    }
  ],
  "hierarchical": [
    {
      "icon": "📜",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>深度信念网络（DBN）</strong>：逐层贪心预训练 RBM，深度学习的前身</li><li><strong>堆叠自编码器（Stacked AE）</strong>：逐层训练 AE，然后把编码器堆叠起来</li><li><strong>ResNet / ViT</strong>：现代深度网络，端到端训练，自然形成层次表示</li><li><strong>U-Net</strong>：跳跃连接把低层细节保留到高层，形成\"横跨层级\"的表示</li></ul>"
    },
    {
      "icon": "🏗️",
      "title": "分层表示的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>深度神经网络之所以\"深\"，核心目的就是学到一个<strong>层次化的表示</strong>：</p>\n<ul class=\"nested-list\"><li><strong>第一层</strong>：边缘、角点、颜色块（Gabor 滤波器类似）</li><li><strong>中间层</strong>：纹理模式、局部形状（眼睛、轮子、窗户）</li><li><strong>高层</strong>：完整的语义概念（人脸、汽车、建筑）</li></ul>\n<p>每一层都是对上一层特征的<strong>组合与抽象</strong>——这正是深度学习的\"深度\"二字的含义。</p>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 理解要点</div><p>分层表示不是某个特定方法的专利——<strong>任何足够深的神经网络都会自发形成层次表示</strong>，前提是有合适的训练信号和足够的深度。</p></div>"
    }
  ],
  "linear-nonlinear": [
    {
      "icon": "📏",
      "title": "本质差别在哪里？",
      "tags": [
        "核心理念"
      ],
      "expanded": true,
      "body": "<table class=\"comp-table\"><tr><th></th><th>线性</th><th>非线性</th></tr><tr><td>公式</td><td><code class=\"code-inline\">Z = WX + b</code></td><td><code class=\"code-inline\">Z = σ(WX + b)</code></td></tr><tr><td>表示空间</td><td>线性子空间（超平面）</td><td>弯曲流形</td></tr><tr><td>捕获的统计量</td><td>二阶（协方差）</td><td>高阶、非欧</td></tr><tr><td>训练方式</td><td>有闭式解（SVD / 矩阵分解）</td><td>需要梯度下降（BP + SGD）</td></tr><tr><td>最优解</td><td>保证全局最优</td><td>不保证（可能陷入局部最优）</td></tr><tr><td>堆叠多层</td><td>等价于一层（线性闭包）</td><td>产生层次抽象</td></tr><tr><td>代表方法</td><td>PCA, SVD, NMF, ICA, LDA</td><td>Deep AE, VAE, SimCLR, ViT</td></tr></table>\n<p>从形式上看，差距确实就一个激活函数——但这个\"差距\"打开了一整个新世界。</p>"
    },
    {
      "icon": "🌀",
      "title": "核技巧：一个有趣的中间地带",
      "tags": [
        "补充"
      ],
      "expanded": false,
      "body": "<p>核技巧让你用线性方法解决非线性问题：</p>\n<p>非线性映射 <code class=\"code-inline\">φ: x → φ(x)</code> 把数据映射到高维→在高维空间做线性方法（SVM, PCA）→但不显式计算 φ(x)，而是用核函数 <code class=\"code-inline\">K(xᵢ, xⱼ) = φ(xᵢ)·φ(xⱼ)</code></p>\n<p>所以它是<strong>形式上的非线性、算法上的线性</strong>——训练方式还是有闭式解（SVD），但也等价于在原始空间学到了一个非线性流形。</p>"
    },
    {
      "icon": "🔬",
      "title": "现代视角：线性探针",
      "tags": [
        "前沿"
      ],
      "expanded": false,
      "body": "<p>一个有趣的反直觉现象：</p>\n<p>现代深度表示学习（CLIP, DINOv2, SimCLR）学到的特征是深度非线性的，但人们用<strong>线性探针</strong>（Linear Probe）——在冻结的特征上只训练一个线性分类器——来评估特征质量。</p>\n<p>如果线性探针效果好，说明非线性的编码器把数据\"拉直\"了，使得数据在最终的特征空间中是<strong>线性可分的</strong>。这本质上是非线性编码器在\"学一个让线性方法有效的空间\"。</p>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 理解要点</div><p>线性 vs 非线性不是非黑即白的——现代方法在<strong>编码阶段用非线性</strong>，在<strong>应用阶段假设线性可分</strong>。最好的非线性，是让数据变\"线性\"的非线性。</p></div>"
    }
  ],
  "metric": [
    {
      "icon": "🎯",
      "title": "代表损失函数与方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>对比损失（Contrastive Loss）</strong>：Siamese 网络，一对样本的距离与阈值比较</li><li><strong>三元组损失（Triplet Loss）</strong>：<code class=\"code-inline\">(anchor, positive, negative)</code> 三元组，让 anchor-positive 距离小于 anchor-negative 距离</li><li><strong>N-pair Loss</strong>：对比多个负样本的扩展</li><li><strong>ArcFace / CosFace</strong>：在 Softmax 中引入角度/余弦余量，人脸识别主流</li><li><strong>ProxyNCA</strong>：为每个类学一个代理（proxy）向量，代替 pairwise 计算</li></ul>"
    },
    {
      "icon": "📏",
      "title": "度量学习的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>和分类不同，度量学习不关心样本属于哪一类，而是关心：<strong>两个样本有多相似？</strong></p>\n<ul class=\"nested-list\"><li>不需要固定的类别集合——可以处理<strong>开放集</strong>（open-set）问题</li><li>学到的嵌入空间具有<strong>泛化性</strong>：新类别的样本也能正确嵌入</li><li>典型应用：人脸识别、行人重识别、图像检索</li></ul>"
    }
  ],
  "multimodal": [
    {
      "icon": "🎯",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>CLIP</strong>：4 亿图文对的对比学习，图文编码器各自独立，用对比损失拉近配对的图文对</li><li><strong>ALIGN</strong>：用噪点更强的图文数据（10 亿对），但方法更简单</li><li><strong>ImageBind</strong>：绑定 6 种模态（图、文、音、热感、深度、IMU）到一个空间</li><li><strong>GPT-4V / Gemini</strong>：多模态大模型，端到端理解图文混合输入</li></ul>"
    },
    {
      "icon": "🌉",
      "title": "多模态表示的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>核心目标：让\"猫\"这个词、猫的照片、猫的叫声在表示空间中<strong>互相对齐</strong>。</p>\n<ul class=\"nested-list\"><li><strong>共享语义空间</strong>：不同模态编码到同一空间，语义相近的样本距离近</li><li><strong>零样本迁移</strong>：在一个模态上学到的概念可以迁移到另一个模态</li><li><strong>跨模态检索</strong>：用文字搜图片、用图片搜文字、用声音搜图片……</li></ul>"
    }
  ],
  "multitask": [
    {
      "icon": "⚖️",
      "title": "关键挑战",
      "tags": [
        "挑战"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>任务冲突</strong>：不同任务的梯度方向不一致，可能导致共享表示难以兼顾</li><li><strong>损失平衡</strong>：不同任务的 loss 量级不同，需要精心调节权重</li><li><strong>负迁移</strong>：当任务不相关时，多任务学习反而损害性能</li><li><strong>解决方法</strong>：PCGrad（投影梯度）、Uncertainty Weighting（不确定性加权）、Task Balancing</li></ul>"
    },
    {
      "icon": "🧩",
      "title": "多任务学习的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>多任务学习（Multi-task Learning, MTL）的核心直觉：</p>\n<ul class=\"nested-list\"><li>多个任务可能有共享的低级特征（边缘、纹理、语法结构）</li><li>共享表示让模型<strong>看到更多样化的训练信号</strong>，从而学到更鲁棒的特征</li><li>任务之间可以<strong>互相提供归纳偏置</strong>——任务 A 的难点可能被任务 B 的信号解决</li></ul>\n<p>典型的例子：同时做语义分割 + 深度估计 + 边缘检测，共享一个编码器，各自接不同的解码头。</p>"
    }
  ],
  "notes": [
    {
      "icon": "🏗️",
      "title": "AE vs U-Net：同一个父亲，不同的母亲",
      "tags": [
        "架构",
        "对照"
      ],
      "expanded": false,
      "body": "<p>用家族比喻来记住它们的关系：</p>\n<p><strong>父亲编码器-解码器架构</strong></p>\n<table class=\"comp-table\"><tr><th></th><th><strong>自编码器</strong></th><th><strong>U-Net</strong></th></tr><tr><td>母亲</td><td>表示学习（自监督）</td><td>密集预测（监督）</td></tr><tr><td>天赋</td><td>学通用特征，可迁移</td><td>像素级对齐，精度高</td></tr><tr><td>弱点</td><td>瓶颈可能丢失细节</td><td>学到的表示难迁移</td></tr><tr><td>比喻</td><td>螺丝刀（干啥都行）</td><td>开瓶器（开瓶一绝）</td></tr></table>"
    },
    {
      "icon": "🔀",
      "title": "对比学习的本质：拉近正推开负",
      "tags": [
        "对比学习"
      ],
      "expanded": false,
      "body": "<p>如果说自编码器的哲学是\"重构就是理解\"，那对比学习的哲学就是<strong>\"区分就是理解\"</strong>。</p>\n<p>它不关心你能不能把一张图重建出来，它只关心你能不能把不同图分开。这造就了截然不同的表示性质：</p>\n<ul class=\"nested-list\"><li>AE 的表示：保留更多像素级信息，利于生成，但可能包含冗余</li><li>对比的表示：天然线性可分，利于分类检索，但可能丢失像素细节</li></ul>"
    },
    {
      "icon": "⚡",
      "title": "线性 vs 非线性：一个激活函数的差距",
      "tags": [
        "核心洞察"
      ],
      "expanded": false,
      "body": "<p>纯从数学形式上看，二者的差距就是<strong>一个激活函数</strong>：</p>\n<ul class=\"nested-list\"><li>线性：Z = WX + b</li><li>非线性：Z = σ(WX + b)</li></ul>\n<p>但这一差展开了八个维度的天壤之别：闭式解 vs 梯度下降、全局最优 vs 局部最优、子空间 vs 流形、一层等于多层 vs 层叠产生抽象……」</p>\n<p>所以即使你已经知道了结果（\"就是加了个激活函数\"），也要理解这个\"就是\"里面包含了多大的张力。表示学习的整个历史，就是不断用非线性挑战线性极限的历史。</p>"
    },
    {
      "icon": "🔭",
      "title": "自监督表示学习三大范式速记",
      "tags": [
        "总览",
        "速记"
      ],
      "expanded": false,
      "body": "<table class=\"comp-table\"><tr><th>范式</th><th>一句话</th><th>代表</th></tr><tr><td>生成式</td><td>\"把砸烂的东西恢复原样\"</td><td>AE, MAE, BERT</td></tr><tr><td>对比式</td><td>\"把一样的拉近、不一样的推开\"</td><td>SimCLR, MoCo, CLIP</td></tr><tr><td>非对比式</td><td>\"两个分支的输出要相关但不能坍塌\"</td><td>BYOL, Barlow Twins, DINO</td></tr></table>"
    },
    {
      "icon": "🤖",
      "title": "自编码器的本质：信息瓶颈",
      "tags": [
        "AE"
      ],
      "expanded": true,
      "body": "<p>自编码器的核心不是\"长得像什么\"，而是<strong>信息必须经过瓶颈</strong>。</p>\n<p>这个瓶颈迫使网络：输入压缩 → 舍弃冗余 → 提取最本质的语义因子 → 解压重构。所有变体（稀疏 AE、去噪 AE、VAE、MAE）都是在这个骨架上加正则化、改损失函数、换层类型。</p>\n<p><strong>没有瓶颈压缩的就不是自编码器</strong>——看看有跳跃连接的结构就知道为什么 U-Net 不是了。</p>"
    },
    {
      "icon": "🧘",
      "title": "非对比式方法的启示：负样本不是必须的",
      "tags": [
        "自监督",
        "关键洞察"
      ],
      "expanded": false,
      "body": "<p>BYOL 和 SimSiam 告诉我们：<strong>你不需要负样本也能避免坍塌</strong>。</p>\n<p>这背后的数学直觉是：不对称网络结构（predictor + stop-gradient / 动量编码器）本身就构成了一种\"隐式负样本\"——因为如果网络坍塌，predictor 就可以完美预测目标网络，结果 predictor 反而不需要学任何东西，导致 loss 不会降低。</p>\n<p>Barlow Twins 更进一步：不需要任何不对称，只需要<strong>让不同维度之间的相关性趋于0</strong>，就能自然避免所有样本映射到同一个点。</p>"
    }
  ],
  "self-supervised": [
    {
      "icon": "📊",
      "title": "三大范式的对比",
      "tags": [
        "对照"
      ],
      "expanded": false,
      "body": "<table class=\"comp-table\"><tr><th></th><th>生成式</th><th>对比式</th><th>非对比式</th></tr><tr><td>代表</td><td>AE, MAE, BERT</td><td>SimCLR, MoCo, CLIP</td><td>BYOL, Barlow Twins, DINO</td></tr><tr><td>监督信号</td><td>重构/预测被破坏部分</td><td>正负样本对的区分</td><td>正样本对的相关性约束</td></tr><tr><td>负样本</td><td>不需要</td><td>需要</td><td>不需要</td></tr><tr><td>学到什么</td><td>数据的分布 / 结构</td><td>判别性边界</td><td>去相关的语义空间</td></tr><tr><td>坍塌风险</td><td>低（有重构目标）</td><td>低（有负样本推开）</td><td>中（靠正则化防坍塌）</td></tr></table>"
    },
    {
      "icon": "🤝",
      "title": "对比式（Contrastive）",
      "tags": [
        "范式"
      ],
      "expanded": false,
      "body": "<p><strong>核心逻辑</strong>：同一张图的不同增强版本（裁剪、旋转、颜色变换）在表示空间里靠近，不同图片推开。</p>\n<ul class=\"nested-list\"><li><strong>SimCLR</strong>：简单的对比学习框架，batch 内互为负样本</li><li><strong>MoCo</strong>：用动量编码器维护一个大的负样本队列</li><li><strong>CLIP</strong>：图文对比，4 亿图文对，零样本迁移能力强</li><li><strong>CPC / CMC</strong>：对比预测编码，跨视角对比</li></ul>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 理解要点</div><p>对比式不关心重建精度，只关心<strong>判别性</strong>——它学到的表示天然是线性可分的，因为训练目标就是\"分开不同样本、聚合同类样本\"。</p></div>"
    },
    {
      "icon": "🔄",
      "title": "生成式（Generative）",
      "tags": [
        "范式"
      ],
      "expanded": true,
      "body": "<p><strong>核心逻辑</strong>：把输入破坏掉，让网络恢复原样。</p>\n<ul class=\"nested-list\"><li><strong>自编码器（AE）</strong>：编码→瓶颈→解码重构。变体包括 VAE、去噪 AE、稀疏 AE</li><li><strong>掩码自编码器（MAE）</strong>：遮住图片大部分 patch，只让编码器看可见部分，解码器重建被遮部分</li><li><strong>自回归预测（GPT）</strong>：预测下一个 token</li><li><strong>掩码语言建模（BERT）</strong>：遮住文本中的词，预测被遮的词</li></ul>\n<div class=\"example-box\"><div class=\"example-box-title\">💡 理解要点</div><p>生成式的核心约束是<strong>信息瓶颈</strong>——网络必须把输入压缩到一个紧凑的表示再解压，这个压缩过程迫使它学到数据的本质结构。</p></div>"
    },
    {
      "icon": "🧘",
      "title": "非对比式 / 冗余消除（Non-contrastive）",
      "tags": [
        "范式"
      ],
      "expanded": false,
      "body": "<p><strong>核心逻辑</strong>：不需要负样本，通过数学约束防止模型坍塌。</p>\n<ul class=\"nested-list\"><li><strong>BYOL</strong>：不对称网络（在线+目标），只用正样本对，目标网络动量更新</li><li><strong>SimSiam</strong>：连 BYOL 的动量都不需要，stop-gradient 就够</li><li><strong>Barlow Twins</strong>：让两个分支输出的互相关矩阵接近单位阵——去相关</li><li><strong>VICReg</strong>：方差 + 协方差 + 均方误差三项约束</li><li><strong>DINO / DINOv2</strong>：自蒸馏 + 中心化 + sharpening，在 ViT 上尤其强大</li></ul>\n<p>非对比式方法<strong>挑战了\"负样本是必要的\"这个假设</strong>，显示出正则化本身就可以防止坍塌。</p>"
    }
  ],
  "semi-supervised": [
    {
      "icon": "🏷️",
      "title": "半监督核心方法",
      "tags": [
        "方法"
      ],
      "expanded": true,
      "body": "<ul class=\"nested-list\"><li><strong>自训练（Self-training）</strong>：用少量标签训练模型 → 给无标签数据打伪标签 → 用伪标签再训练</li><li><strong>一致性正则化（Consistency Regularization）</strong>：同一样本的不同增强版本应有相同的预测（FixMatch, MixMatch）</li><li><strong>半监督自编码器</strong>：在 AE 的重构损失之上加分类损失，共享编码器（SSVAE）</li><li><strong>Noisy Student</strong>：用噪声注入训练学生模型，让学生超越老师</li></ul>\n<p>本质上，半监督 = <strong>无监督/自监督的信号 + 少量监督信号的联合驱动</strong>。</p>"
    }
  ],
  "sequence": [
    {
      "icon": "🔤",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>LSTM / GRU</strong>：门控循环网络，通过门控机制缓解长程梯度消失</li><li><strong>Transformer</strong>：自注意力机制，直接建模任意位置的依赖关系，位置编码替代顺序</li><li><strong>BERT</strong>：双向 Transformer + 掩码语言建模，学到的上下文表示可用于多种 NLP 任务</li><li><strong>GPT</strong>：单向 Transformer + 自回归预测，学到的表示适合生成任务</li><li><strong>RNN 自编码器</strong>：用 LSTM/GRU 做编码器解码器，适合序列到序列的重构和翻译</li></ul>"
    },
    {
      "icon": "⏳",
      "title": "序列表示的核心挑战",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<ul class=\"nested-list\"><li><strong>变长输入</strong>：序列长度不定，表示需要压缩到固定维度</li><li><strong>长程依赖</strong>：序列远端元素之间的依赖关系（例：句子开头的词影响句尾的时态）</li><li><strong>位置编码</strong>：同一个词在句首和句尾含义不同，需要位置信息</li></ul>"
    }
  ],
  "sparse": [
    {
      "icon": "📚",
      "title": "代表方法",
      "tags": [
        "方法"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>稀疏自编码器（SAE）</strong>：在 AE 的瓶颈层加稀疏约束，让潜在表示大多数维接近 0</li><li><strong>LASSO 回归</strong>：线性模型 + L1 正则化，本质上是稀疏线性表示</li><li><strong>字典学习（Dictionary Learning）</strong>：学习一组过完备基，每个样本只用少数基的线性组合表示</li><li><strong>Sparse Coding</strong>：神经科学启发的无监督方法，每个图像 patch 用少数基原子编码</li></ul>"
    },
    {
      "icon": "🌵",
      "title": "稀疏表示的核心思想",
      "tags": [
        "理念"
      ],
      "expanded": true,
      "body": "<p>认知科学启示：大脑中只有约 1-4% 的神经元同时活跃。稀疏表示追求类似的效果：</p>\n<ul class=\"nested-list\"><li>每个输入只激活潜在空间中的<strong>一小部分维度</strong></li><li>被激活的维度具有<strong>高度的选择性</strong>（每个维度只对特定的输入模式响应）</li><li>稀疏性提升了<strong>可解释性</strong>——你可以直接看出是哪些特征被激活了</li></ul>\n<p>数学上通过在损失函数中加入 L1 正则化（或 KL 散度约束）来实现：</p>\n<p>$$\\mathcal{L} = \\|X - X'\\|^2 + \\lambda \\sum_j |z_j|$$</p>"
    }
  ],
  "supervised": [
    {
      "icon": "🏛️",
      "title": "ImageNet 预训练范式",
      "tags": [
        "经典"
      ],
      "expanded": true,
      "body": "<p>在 ImageNet（1000 类、1400 万张图）上训练一个分类网络，训练完成后，<strong>去掉最后的分类头，把倒数第二层的特征向量当作通用表示</strong>。</p>\n<p>这个范式统治了 CV 领域近十年（2012–2020）：</p>\n<ul class=\"nested-list\"><li>模型演进：AlexNet → VGG → Inception → ResNet → EfficientNet → ViT</li><li>在任意下游任务上，冻结特征 + 线性分类器，就能取得远好于手工特征的效果</li><li>缺点是需要<strong>大量标注数据</strong>，且学到的表示可能过拟合到 ImageNet 的类别分布</li></ul>"
    },
    {
      "icon": "⚖️",
      "title": "监督表示的特性",
      "tags": [
        "理解"
      ],
      "expanded": false,
      "body": "<p>监督信号驱动的表示有一个隐含假设：<strong>分类任务需要的特征也是其他任务需要的特征</strong>。这在很多时候成立（物体的边缘、纹理、形状是通用的），但并非总是成立。</p>\n<p>例如 ImageNet 预训练的特征在医学影像、卫星图上效果明显下降——因为监督信号\"偏置\"了表示去关注对 1000 类分类有用的特征，而不是通用的视觉特征。</p>"
    }
  ],
  "transfer": [
    {
      "icon": "⚙️",
      "title": "迁移学习的调式",
      "tags": [
        "技术"
      ],
      "expanded": false,
      "body": "<ul class=\"nested-list\"><li><strong>全量微调</strong>：所有层都更新，效果最好但计算成本高</li><li><strong>头部微调</strong>：只更新最后几层，适合预训练充分且目标数据少</li><li><strong>Adapter / LoRA</strong>：插入少量可训练参数，冻结预训练权重——参数高效微调（PEFT）</li><li><strong>Prompt Tuning</strong>：不修改模型参数，只在输入前加可学习的\"提示\"向量</li><li><strong>Zero-shot</strong>：不做任何训练直接推理（如 CLIP），依赖多模态对齐</li></ul>"
    },
    {
      "icon": "🔄",
      "title": "预训练 + 微调范式",
      "tags": [
        "方法"
      ],
      "expanded": true,
      "body": "<p>这是当前迁移表示学习的主流范式：</p>\n<ol class=\"nested-list\"><li><strong>预训练</strong>：在大规模数据上训练一个模型（有监督或自监督），得到一个通用的特征提取器</li><li><strong>微调</strong>：在目标任务上，用少量数据微调预训练模型的全参数或最后几层</li><li><strong>线性探针</strong>：冻结特征提取器，只训练一个线性分类器——用于评估预训练特征的质量</li></ol>\n<p>关键变量：<strong>什么时候微调有效？</strong> 预训练和目标任务的数据分布越接近，迁移效果越好。当分布差异大时（如自然图像 → 医学图像），效果会显著下降。</p>"
    }
  ],
  "unsupervised": [
    {
      "icon": "🌀",
      "title": "流形学习",
      "tags": [
        "非线性",
        "可视化"
      ],
      "expanded": false,
      "body": "<p>假设高维数据实际上位于一个低维流形上，通过保持局部邻域结构来\"展开\"这个流形。</p>\n<ul class=\"nested-list\"><li><strong>LLE（局部线性嵌入）</strong>：每个点用邻居线性重构，保持重构权重</li><li><strong>Isomap</strong>：测地线距离替代欧氏距离</li><li><strong>t-SNE</strong>：保持高维和低维概率分布相似，可视化金标准</li><li><strong>UMAP</strong>：t-SNE 的现代替代品，更快、全局结构保持更好</li></ul>\n<p><strong>重要局限</strong>：这些方法没有显式编码器（不能直接处理新样本），且主要用于可视化而非迁移学习。</p>"
    },
    {
      "icon": "📉",
      "title": "经典无监督方法",
      "tags": [
        "线性",
        "统计"
      ],
      "expanded": true,
      "body": "<ul class=\"nested-list\"><li><strong>PCA（主成分分析）</strong>：找到方差最大的方向投影，等价于线性自编码器</li><li><strong>SVD / LSA</strong>：矩阵分解用于文本的潜在语义分析</li><li><strong>ICA（独立成分分析）</strong>：找出统计独立的源信号，用于盲源分离</li><li><strong>NMF（非负矩阵分解）</strong>：分解为两个非负低秩矩阵，可解释性强（\"部分构成整体\"）</li><li><strong>K-means / 谱聚类</strong>：聚类得到的分配向量可以视为一种表示</li><li><strong>RBM / DBN</strong>：受限玻尔兹曼机，深度信念网络的构建块</li></ul>\n<p>这些方法在深度学习兴起前是表示学习的主力，今天的自监督方法在性能上已经大幅超越它们，但它们<strong>可解释性强、有闭式解、计算效率高</strong>，在某些场景仍有不可替代的价值。</p>"
    }
  ]
};
