# 预测容器（Prediction Container）

一句话简介：Container 是 Prediction 模块的数据管理单元，负责存储和更新每个障碍物的历史轨迹、特征和上下文信息，为 Evaluator 和 Predictor 提供完整的输入数据。

## 核心概念/原理

Container 核心功能：
- **障碍物追踪**：按 ID 关联 Perception 输出的连续帧障碍物
- **轨迹缓存**：存储最近 N 帧（通常 10-20 帧）的位置、速度、朝向
- **特征提取**：从轨迹中提取速度、加速度、曲率、交互特征
- **生命周期管理**：处理障碍物出现、消失、ID 切换

## Apollo-Lite 中的实现位置

- Container：`modules/prediction/container/`
- 障碍物管理：`modules/prediction/container/obstacles_container.cc/.h`

## 关键配置

```protobuf
container_conf {
  history_size: 20          # 保留历史帧数
  min_history_size: 10      # 最小有效历史帧数
  max_id_gap: 3             # 允许 ID 跳变最大帧数
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 历史轨迹不足 | 障碍物刚出现或频繁消失 | 检查 `min_history_size` 阈值 |
| ID 跳变频繁 | 感知跟踪不稳定 | 调低 `max_id_gap`，或优化感知跟踪器 |
| 特征异常 | 坐标系转换错误 | 确认 localization 和 perception 坐标系一致 |

## 与其他模块的接口

- **perception**：接收 `PerceptionObstacles` 作为输入
- **prediction/evaluator**：提供障碍物历史轨迹和特征
- **prediction/predictor**：提供完整上下文用于轨迹生成
