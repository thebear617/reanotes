---
icon: 🧘
title: 非对比式 / 冗余消除（Non-contrastive）
tags: [范式]
expanded: false
---

**核心逻辑**：不需要负样本，通过数学约束防止模型坍塌。

- **BYOL**：不对称网络（在线+目标），只用正样本对，目标网络动量更新
- **SimSiam**：连 BYOL 的动量都不需要，stop-gradient 就够
- **Barlow Twins**：让两个分支输出的互相关矩阵接近单位阵——去相关
- **VICReg**：方差 + 协方差 + 均方误差三项约束
- **DINO / DINOv2**：自蒸馏 + 中心化 + sharpening，在 ViT 上尤其强大

非对比式方法**挑战了"负样本是必要的"这个假设**，显示出正则化本身就可以防止坍塌。
