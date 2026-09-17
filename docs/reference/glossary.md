# 符号与术语

本书统一使用行向量右乘矩阵。引用材料有时采用列向量；阅读时先核对形状，再比较公式。

## 常用符号

| 符号 | 含义 | 常见形状 |
| --- | --- | --- |
| $B,T,V$ | batch 大小、序列长度、词表大小 | 标量 |
| $d,d_h$ | 残差宽度、注意力头宽度 | 标量 |
| $R,r_t$ | 残差流、位置 $t$ 的残差 | $T\times d$、$d$ |
| $W_E,W_U$ | 嵌入与反嵌入矩阵 | $V\times d$、$d\times V$ |
| $W_Q,W_K,W_V$ | 查询、键、值投影 | $d\times d_h$ |
| $W_O$ | 一个头的输出投影 | $d_h\times d$ |
| $A$ | 注意力矩阵；行是目标、列是来源 | $T\times T$ |
| $\ell,p$ | logits 与概率 | $V$ |
| $x_c,x_r$ | 参考输入与对照输入 | 随任务而定 |
| $m_c,m_r,m_p$ | 参考、对照、修补运行的指标 | 标量 |
| $z,W_e,W_d$ | SAE 编码、编码矩阵、解码矩阵 | $m$、$d\times m$、$m\times d$ |
| $\lambda$ | 稀疏惩罚强度 | 非负标量 |

## 中英对照

| 中文 | 英文 | 本书中的含义 |
| --- | --- | --- |
| 机制可解释性 | mechanistic interpretability | 研究模型内部计算如何产生行为 |
| 激活 | activation | 一次前向运行中的中间数值 |
| 表征 | representation | 模型用数值组织信息的方式 |
| 特征 | feature | 希望分析的数据属性或计算变量；不自动等于神经元 |
| 神经元 | neuron | 架构中的一个坐标或单元 |
| 回路 | circuit | 共同实现某项计算的组件与依赖关系 |
| 残差流 | residual stream | Transformer 中组件不断读取和加写的状态 |
| 分词单元 | token | 分词器词表中的单元，不保证等于词或汉字 |
| 反嵌入 | unembedding | 从残差向量映射到词表 logits |
| 线性探针 | linear probe | 对冻结激活训练的线性读出器 |
| 消融 | ablation | 将组件活动替换为零、均值或其他基线 |
| 激活修补 | activation patching | 用另一轮运行的激活替换指定中间状态 |
| 路径修补 | path patching | 控制反事实变化沿指定路径传播 |
| 归纳头 | induction head | 参与上下文中的前缀匹配与后继复制的头 |
| 间接宾语识别 | indirect object identification, IOI | 本书中一类名字角色识别任务 |
| 叠加 | superposition | 多于表示维度的特征共享非正交方向的现象或假说 |
| 多义性 | polysemanticity | 一个神经元或隐元响应多种模式 |
| 稀疏自编码器 | sparse autoencoder, SAE | 用稀疏宽编码重构输入激活的模型 |
| 隐元 | latent | SAE 编码空间中的一个坐标；未经验证不直接称为真实概念 |
| 忠实性 | faithfulness | 在指定指标与干预下，解释保留原模型行为的程度 |
| 完备性 | completeness | 是否遗漏了与目标行为相关的重要机制 |
| 最小性 | minimality | 解释中是否包含可去掉的冗余组件，依赖测试定义 |
| 分布外 | out of distribution, OOD | 偏离研究中所依赖的数据或状态分布 |

## 容易混淆的几组词

“相关”不等于“因果”；“可解码”不等于“被使用”；“方向”不等于“坐标轴”；“稀疏”不等于“语义清楚”；“局部恢复”不等于“完整回路”。当结论里出现这些词时，回到实验定义再核对一次。
