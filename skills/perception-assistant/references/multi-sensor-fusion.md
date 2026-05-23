# Apollo 多传感器融合参考

## 融合架构

Apollo-lite perception fusion 采用目标级融合：

```
Camera Perception (2D/3D obstacles)
  \
   \
    → Fusion Module → /apollo/perception/obstacles
   /
LiDAR Perception (3D obstacles)
  /
Radar Perception (objects with velocity)
```

## 融合模块配置

```protobuf
// modules/perception/fusion/conf/fusion_config.pb.txt
fusion_config {
  // 传感器输入
  sensor_sources {
    sensor_type: CAMERA
    sensor_id: "front_6mm"
    topic: "/apollo/perception/camera/front_6mm"
  }
  sensor_sources {
    sensor_type: LIDAR
    sensor_id: "lidar128"
    topic: "/apollo/perception/lidar/lidar128"
  }
  sensor_sources {
    sensor_type: RADAR
    sensor_id: "front_radar"
    topic: "/apollo/perception/radar/front"
  }
  
  // 融合策略
  fusion_method: "PROBABILISTIC_FUSION"
  
  // 时序对齐窗口
  temporal_alignment_window_ms: 100
}
```

## 时空同步

### 时间同步

```cpp
// Cyber RT Header 中的时间戳
message Header {
  optional double timestamp_sec = 1;    // 秒级时间戳
  optional string module_name = 2;     // 发布模块
  optional uint32 sequence_num = 3;     // 序列号
  optional uint64 lidar_timestamp = 4;  // LiDAR 原始时间戳
  optional uint64 camera_timestamp = 5; // Camera 原始时间戳
}
```

**同步策略**:
- 以 LiDAR 时间为基准（10Hz）
- Camera 数据（30Hz）插值到 LiDAR 时间点
- Radar 数据（20Hz）最近邻匹配

### 坐标转换

```cpp
// 统一转换到车辆坐标系（IMU 中心）
Eigen::Vector3d TransformToVehicle(
    const Eigen::Vector3d& point,
    const std::string& sensor_frame_id) {
  
  // 查询 TF
  Eigen::Affine3d sensor_to_vehicle;
  tf_buffer_->lookupTransform("vehicle", sensor_frame_id, 
                              ros::Time(0), sensor_to_vehicle);
  
  return sensor_to_vehicle * point;
}
```

## 数据关联算法

### 匈牙利算法 + IoU 关联

```cpp
// 代价矩阵：1 - IoU
double cost = 1.0 - ComputeIoU(camera_box, lidar_box);

// 匈牙利求解最优分配
HungarianSolver::Solve(cost_matrix, &assignments);
```

### 关联门限

| 传感器对 | 距离阈值 | IoU 阈值 | 说明 |
|---------|---------|---------|------|
| Camera-LiDAR | 2.0m | 0.3 | 近距严格 |
| Camera-Radar | 3.0m | - | 雷达无框 |
| LiDAR-Radar | 2.5m | 0.2 | 中距 |

## 融合质量评估

| 指标 | 计算方法 | 目标 |
|------|---------|------|
| 融合精度 | 与真值位置差 | < 0.3m |
| 融合召回 | 真值目标被融合比例 | > 95% |
| 融合一致性 | 跨帧目标 ID 稳定 | > 98% |
| 时延 | 端到端延迟 | < 150ms |

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| 融合目标抖动 | 传感器间切换主导 | 增加融合平滑滤波 |
| 目标分裂 | 多传感器检测同一目标 | 调整关联阈值 |
| 时延大 | 时间同步窗口过大 | 减小 temporal_alignment_window |
| 远处目标丢失 | LiDAR 稀疏 + Camera 小目标 | 增加 Radar 权重 |
| 类别不一致 | Camera=car, LiDAR=truck | 以 Camera 分类为准 |
