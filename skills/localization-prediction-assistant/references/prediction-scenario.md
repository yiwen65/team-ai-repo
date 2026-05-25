# 预测场景分类（Prediction Scenario）

一句话简介：Scenario 模块根据障碍物当前位置和地图拓扑，将其分类到特定场景（如 OnLane、Junction、Parking），从而选择合适的 Evaluator-Predictor 组合策略。

## 核心概念/原理

场景分类逻辑：
- **OnLane**：障碍物在车道上正常行驶（最常见）
- **Junction**：障碍物在路口范围内
- **Parking**：障碍物在停车区域
- **Emergency**：异常状态（如逆行、静止在车道）

分类依据：
- 障碍物到最近车道的距离
- 是否在 junction 多边形内
- 速度大小和方向
- 与周围障碍物的交互关系

## Apollo-Lite 中的实现位置

- Scenario 模块：`modules/prediction/scenario/`
- 场景分析器：`modules/prediction/scenario/scenario_analyzer.cc/.h`

## 关键配置

```protobuf
scenario_conf {
  junction_range: 15.0       # junction 判定范围 (m)
  lane_threshold: 2.0        # 偏离车道阈值 (m)
  stop_speed_threshold: 0.5   # 静止判定阈值 (m/s)
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 路口场景误判 | junction 边界定义不准 | 核对 HDMap junction 多边形 |
| 场景频繁切换 | 阈值设置过严 | 增加 hysteresis 滞后窗口 |
| 停车场景漏检 | parking 区域未标注 | 检查地图 parking space 图层 |

## 与其他模块的接口

- **map/hdmap**：提供车道和 junction 几何信息
- **prediction/evaluator**：Scenario 决定使用哪个 Evaluator
- **prediction/predictor**：不同场景使用不同的 Predictor 参数
