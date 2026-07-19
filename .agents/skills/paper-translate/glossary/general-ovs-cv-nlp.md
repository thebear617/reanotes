# 通用 OVS / CV / NLP 术语表

> Skill 内置 fallback 术语表。给一篇没有自带术语表的论文时用。
> 优先级低于调用方通过 `--glossary` 传入的项目专属术语表。

| EN                                          | 中文                                             |
| ------------------------------------------- | ------------------------------------------------ |
| open-vocabulary                             | 开放词汇                                         |
| open-vocabulary semantic segmentation (OVS) | 开放词汇语义分割                                 |
| open-vocabulary detection                   | 开放词汇检测                                     |
| open-vocabulary instance segmentation       | 开放词汇实例分割                                 |
| open-vocabulary panoptic segmentation       | 开放词汇全景分割                                 |
| vision-language model (VLM)                 | 视觉-语言模型                                    |
| vision-language pre-training (VLP)          | 视觉-语言预训练                                  |
| large language model (LLM)                  | 大语言模型                                       |
| large multimodal model (LMM)                | 大多模态模型                                     |
| foundation model                            | 基础模型                                         |
| pre-training                                | 预训练                                           |
| fine-tuning                                 | 微调                                             |
| prompt tuning                               | 提示调优                                         |
| prompt engineering                          | 提示工程                                         |
| zero-shot                                   | 零样本                                           |
| few-shot                                    | 少样本                                           |
| training-free                               | 免训练                                           |
| weakly-supervised                           | 弱监督                                           |
| fully-supervised                            | 全监督                                           |
| self-supervised                             | 自监督                                           |
| contrastive learning                        | 对比学习                                         |
| masked image modeling                       | 掩码图像建模                                     |
| masked language modeling                    | 掩码语言建模                                     |
| image-text matching                         | 图文匹配                                         |
| image-text contrastive learning             | 图文对比学习                                     |
| cross-modal                                 | 跨模态                                           |
| cross-attention                             | 交叉注意力                                       |
| self-attention                              | 自注意力                                         |
| multi-head attention                        | 多头注意力                                       |
| multi-modal                                 | 多模态                                           |
| encoder                                     | 编码器                                           |
| decoder                                     | 解码器                                           |
| transformer                                 | Transformer                                      |
| vision transformer (ViT)                    | Vision Transformer / 视觉 Transformer            |
| CNN / convolutional neural network          | 卷积神经网络                                     |
| ResNet                                      | ResNet（保留英文）                               |
| CLIP                                        | CLIP（保留英文）                                 |
| alignment                                   | 对齐                                             |
| embedding                                   | 嵌入                                             |
| feature map                                 | 特征图                                           |
| feature pyramid                             | 特征金字塔                                       |
| patch                                       | 图块                                             |
| token                                       | 词元 / token（首次出现保留英文）                 |
| positional encoding                         | 位置编码                                         |
| mask                                        | 掩码                                             |
| region proposal                             | 区域提议                                         |
| bounding box                                | 边界框                                           |
| anchor                                      | 锚框                                             |
| non-maximum suppression (NMS)               | 非极大值抑制                                     |
| mean average precision (mAP)                | 平均精度均值                                     |
| intersection over union (IoU)               | 交并比                                           |
| pixel accuracy                              | 像素准确率                                       |
| mean IoU (mIoU)                             | 平均交并比                                       |
| prompt                                      | 提示                                             |
| class-agnostic                              | 与类别无关                                       |
| class-agnostic mask                         | 与类别无关的掩码                                 |
| classifier                                  | 分类器                                           |
| classifier weight                           | 分类器权重                                       |
| classification weight                       | 分类权重                                         |
| semantic                                    | 语义                                             |
| instance                                    | 实例                                             |
| panoptic                                    | 全景                                             |
| stuff / thing                               | stuff / thing（背景类 / 前景类，保留英文并加注） |
| base class                                  | 基础类                                           |
| novel class                                 | 新类                                             |
| seen class                                  | 已见类                                           |
| unseen class                                | 未见类                                           |
| benchmark                                   | 基准                                             |
| dataset                                     | 数据集                                           |
| annotation                                  | 标注                                             |
| inference                                   | 推理                                             |
| backbone                                    | 主干网络                                         |
| neck                                        | 颈部网络                                         |
| head                                        | 头部网络                                         |
| decoder head                                | 解码头                                           |
| segmentation head                           | 分割头                                           |
| distillation                                | 蒸馏                                             |
| knowledge distillation                      | 知识蒸馏                                         |
| pseudo-label                                | 伪标签                                           |
| pseudo-mask                                 | 伪掩码                                           |
| teacher / student                           | 教师 / 学生                                      |
| offline / online                            | 离线 / 在线                                      |
| gradient                                    | 梯度                                             |
| learning rate                               | 学习率                                           |
| batch size                                  | 批大小                                           |
| epoch                                       | 轮次                                             |
| checkpoint                                  | 检查点                                           |
| weight decay                                | 权重衰减                                         |
| data augmentation                           | 数据增强                                         |
| random crop                                 | 随机裁剪                                         |
| random flip                                 | 随机翻转                                         |
| color jitter                                | 颜色抖动                                         |
| ablation study                              | 消融实验                                         |
| state-of-the-art (SOTA)                     | 当前最优                                         |
| baseline                                    | 基线                                             |
| quantitative / qualitative                  | 定量 / 定性                                      |
| downstream task                             | 下游任务                                         |
| transfer learning                           | 迁移学习                                         |
| generalizability                            | 泛化能力                                         |
| attention map                               | 注意力图                                         |
| affinity                                    | 亲和度                                           |
| affinity matrix                             | 亲和度矩阵                                       |
| cosine similarity                           | 余弦相似度                                       |
| dot product                                 | 点积                                             |
| logits                                      | logits（保留英文）                               |
| softmax                                     | softmax（保留英文）                              |
| sigmoid                                     | sigmoid（保留英文）                              |
| argmax                                      | argmax（保留英文）                               |
| negative pair                               | 负样本对                                         |
| positive pair                               | 正样本对                                         |
| queue                                       | 队列                                             |
| momentum encoder                            | 动量编码器                                       |
| momentum update                             | 动量更新                                         |
| image encoder                               | 图像编码器                                       |
| text encoder                                | 文本编码器                                       |
| text embedding                              | 文本嵌入                                         |
| image embedding                             | 图像嵌入                                         |
| class embedding                             | 类别嵌入                                         |
| category name                               | 类别名                                           |
| class name                                  | 类名                                             |
| noun                                        | 名词                                             |
| caption                                     | 描述 / 图注                                      |
| prompt template                             | 提示模板                                         |
| "a photo of a {class}"                      | "一张 {class} 的照片"                            |
| learnable prompt                            | 可学习提示                                       |
| prompt ensemble                             | 提示集成                                         |
| per-pixel classification                    | 逐像素分类                                       |
| patch-level classification                  | 图块级分类                                       |
| region-level classification                 | 区域级分类                                       |
| grouping                                    | 分组                                             |
| merge                                       | 合并                                             |
| mask refinement                             | 掩码精修                                         |
| class token                                 | 类别 token                                       |
| patch token                                 | 图块 token                                       |
| background                                  | 背景                                             |
| foreground                                  | 前景                                             |
| over-segmentation                           | 过度分割                                         |
| under-segmentation                          | 分割不足                                         |
| receptive field                             | 感受野                                           |
| stride                                      | 步幅                                             |
| padding                                     | 填充                                             |
| upsample / downsample                       | 上采样 / 下采样                                  |
| skip connection                             | 跳跃连接                                         |
| residual connection                         | 残差连接                                         |
| layer normalization (LayerNorm)             | 层归一化                                         |
| batch normalization (BatchNorm)             | 批归一化                                         |
| GELU                                        | GELU（保留英文）                                 |
| ReLU                                        | ReLU（保留英文）                                 |
| parameter                                   | 参数                                             |
| hyperparameter                              | 超参数                                           |
| end-to-end                                  | 端到端                                           |
| pipeline                                    | 流水线                                           |
| framework                                   | 框架                                             |
| repository                                  | 仓库                                             |
| GPU / TPU                                   | GPU / TPU（保留英文）                            |
| floating point operations (FLOPs)           | 浮点运算次数                                     |
| memory footprint                            | 显存占用                                         |
| inference time                              | 推理时间                                         |
| throughput                                  | 吞吐                                             |
| latency                                     | 延迟                                             |
| per-class IoU                               | 单类 IoU                                         |
| confusion matrix                            | 混淆矩阵                                         |
| rare class                                  | 罕见类                                           |
| common class                                | 常见类                                           |
| long-tail                                   | 长尾                                             |
| synonym                                     | 同义词                                           |
| hypernym                                    | 上位词                                           |
| noun phrase                                 | 名词短语                                         |
| word embedding                              | 词嵌入                                           |
| BERT                                        | BERT（保留英文）                                 |
| GPT                                         | GPT（保留英文）                                  |
| LLaMA                                       | LLaMA（保留英文）                                |
| Q-Former                                    | Q-Former（保留英文）                             |
| Perceiver                                   | Perceiver（保留英文）                            |
