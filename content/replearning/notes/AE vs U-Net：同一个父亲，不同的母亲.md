---
icon: 🏗️
title: AE vs U-Net：同一个父亲，不同的母亲
tags: [架构, 对照]
expanded: false
---

用家族比喻来记住它们的关系：

<table class="comp-table">
  <tr><td></td><td><strong>自编码器</strong></td><td><strong>U-Net</strong></td></tr>
  <tr><td>父亲</td><td colspan="2" style="text-align:center">编码器-解码器架构</td></tr>
  <tr><td>母亲</td><td>表示学习（自监督）</td><td>密集预测（监督）</td></tr>
  <tr><td>天赋</td><td>学通用特征，可迁移</td><td>像素级对齐，精度高</td></tr>
  <tr><td>弱点</td><td>瓶颈可能丢失细节</td><td>学到的表示难迁移</td></tr>
  <tr><td>比喻</td><td>螺丝刀（干啥都行）</td><td>开瓶器（开瓶一绝）</td></tr>
</table>
