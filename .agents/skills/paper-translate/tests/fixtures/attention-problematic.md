# Attention Is All You Need

## Abstract

An attention-only sequence transduction architecture.

## Results

<table><tr><td rowspan="2">Model</td><td colspan="2">BLEU</td></tr><tr><td>EN-DE</td><td>EN-FR</td></tr><tr><td>Transformer</td><td>$27.3$</td><td>$38.1$</td></tr></table>

$$
l r a t e = d _ { \mathrm { m o d e l } } ^ { - 0 . 5 }
\cdot m i n ( s t e p _ { - } n u m ^ { - 0 . 5 }, 1 0 ^ { - 9 } )
$$

![](images/attention.jpg) Figure 2: Scaled dot-product and multi-head attention.
