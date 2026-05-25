# 深度学习预测网络

一句话简介：Apollo-Lite Prediction 模块集成深度学习模型（如 CNN/LSTM/Transformer），通过历史轨迹和地图特征端到端预测障碍物未来轨迹，提升复杂场景（如路口、变道）的预测精度。

## 核心概念/原理

Network 预测流程：
1. **特征编码**：将障碍物历史轨迹、周围障碍物、地图车道线编码为张量
2. **模型推理**：神经网络输出未来位置的概率分布或多模态轨迹
3. **后处理**：将模型输出转换为 Apollo `Trajectory` 格式，施加物理约束

模型类型：
- **Social LSTM**：建模多智能体交互
- **VectorNet**：向量化地图和轨迹表示
- **TNT (Target-driven NMT)**：目标点驱动的轨迹生成

## Apollo-Lite 中的实现位置

- 网络模块：`modules/prediction/network/`
- 模型加载：`modules/prediction/network/net_model.cc/.h`
- 推理引擎：`modules/prediction/prediction_component.cc` 调用网络

## 关键配置

```protobuf
network_conf {
  model_path: "/apollo/modules/prediction/data/model.pt"
  use_gpu: true
  batch_size: 1
  input_dim: 128
  output_dim: 64
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 模型加载失败 | 路径错误/版本不匹配 | 检查 `model_path` 和模型文件存在性 |
| 推理延迟高 | GPU 占用高/模型过大 | 启用 TensorRT 或降低 batch_size |
| 预测偏差大 | 训练数据分布差异 | 检查输入特征归一化参数是否与训练一致 |
| 多模态轨迹发散 | 温度参数过高 | 降低采样温度，增加轨迹聚类后处理 |

## 与其他模块的接口

- **prediction/container**：获取编码所需的障碍物特征
- **map/pnc_map**：获取地图车道线向量化表示
- **deployment**：模型文件通过 Bazel 打包或 OTA 更新部署
