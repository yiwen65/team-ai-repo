# 轨迹预测（Prediction Predictor）

一句话简介：Predictor 根据 Evaluator 输出的意图概率，生成障碍物未来一段时间（通常 3-8 秒）的预测轨迹，供 Planning 模块进行碰撞检测和避让决策。

## 核心概念/原理

Predictor 类型：
- **LaneSequence Predictor**：沿 lane sequence 生成平滑轨迹
- **FreeMove Predictor**：基于运动学模型的自由运动预测
- **Interaction Predictor**：考虑多障碍物交互的联合预测
- **Extrapolation Predictor**：简单外推（用于低置信度场景）

轨迹约束：
- 最大加速度/减速度
- 最大曲率（车辆动力学约束）
- 与车道边界保持安全距离

## Apollo-Lite 中的实现位置

- Predictor 基类：`modules/prediction/predictor/`
- LaneSequence：`modules/prediction/predictor/lane_sequence/`
- FreeMove：`modules/prediction/predictor/free_move/`
- Interaction：`modules/prediction/predictor/interaction/`

## 关键配置

```protobuf
predictor_conf {
  prediction_time_length: 8.0    # 预测时长 (s)
  prediction_period: 0.1         # 预测步长 (s)
  max_acceleration: 3.0          # 最大加速度 (m/s²)
  max_deceleration: -4.0        # 最大减速度 (m/s²)
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 轨迹曲率过大 | 预测模型未考虑车辆动力学 | 检查曲率约束参数 |
| 预测轨迹抖动 | 输入历史轨迹噪声大 | 平滑输入轨迹，降低高频噪声 |
| 与规划轨迹冲突 | 预测保守度设置不当 | 调整预测时长和不确定性椭圆 |

## 与其他模块的接口

- **prediction/evaluator**：获取意图概率分布
- **planning**：`PredictionObstacles` 是 Planning 的核心输入之一
