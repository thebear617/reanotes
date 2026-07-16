---
title: 度量学习
icon: ruler-combined
---

学习一个语义相似样本距离近、语义不同样本距离远的嵌入空间。

## 度量学习的核心思想

和分类不同，度量学习不关心样本属于哪一类，而是关心：**两个样本有多相似？**

- 不需要固定的类别集合——可以处理**开放集**（open-set）问题
- 学到的嵌入空间具有**泛化性**：新类别的样本也能正确嵌入
- 典型应用：人脸识别、行人重识别、图像检索

## 代表损失函数与方法

- **对比损失（Contrastive Loss）**：Siamese 网络，一对样本的距离与阈值比较
- **三元组损失（Triplet Loss）**：`(anchor, positive, negative)` 三元组，让 anchor-positive 距离小于 anchor-negative 距离
- **N-pair Loss**：对比多个负样本的扩展
- **ArcFace / CosFace**：在 Softmax 中引入角度/余弦余量，人脸识别主流
- **ProxyNCA**：为每个类学一个代理（proxy）向量，代替 pairwise 计算
