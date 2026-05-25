# 意图评估（Prediction Evaluator）

一句话简介：Evaluator 分析障碍物历史轨迹和场景上下文，评估其未来意图（如变道、直行、停车、交互），为 Predictor 选择最合适的预测模型。

## 核心概念/原理

Evaluator 分类：
- **LaneSequence Evaluator**：评估障碍物在各 lane sequence 上的概率（最常用）
- **FreeMove Evaluator**：无车道约束场景（如停车场、路口中心）
- **Junction Evaluator**：路口场景下的意图分类
- **Interaction Evaluator**：多障碍物交互场景

评估方法：
- 基于规则的启发式评分
- 基于深度学习的概率预测
- 混合方法（规则 + 模型）

## Apollo-Lite 中的实现位置

- Evaluator 基类：`modules/prediction/evaluator/`
- LaneSequence：`modules/prediction/evaluator/vehicle/`
- Junction：`modules/prediction/evaluator/junction/`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 意图概率异常 | 车道线检测不准 | 检查 perception lane 输出质量 |
| 路口意图错误 | junction 拓扑不完整 | 核对 HDMap junction 定义 |
| 交互评估偏差 | 周围障碍物轨迹不完整 | 检查 container 中所有相关障碍物的历史 |

## 与其他模块的接口

- **prediction/container**：获取障碍物历史轨迹
- **prediction/scenario**：根据场景类型选择 Evaluator
- **prediction/predictor**：Evaluator 输出概率分布指导 Predictor 生成轨迹
