# Apollo LiDAR 感知参考

## 支持的雷达型号

Apollo-lite drivers/lidar 支持多种 LiDAR：

| 品牌 | 型号 | 线数 | 点频 | 接口 |
|------|------|------|------|------|
| Hesai | Pandar64/128 | 64/128 | ~240万pts/s | Ethernet |
| Livox | Mid-360/HAP | 固态 | ~20万pts/s | Ethernet |
| Velodyne | VLP-16/32/64/128 | 16/32/64/128 | ~60-300万pts/s | Ethernet |
| Robosense | RS-LiDAR-M1/Helios | 32/128 | ~200万pts/s | Ethernet |
| Seyond | Falcon | 固态 | ~15万pts/s | Ethernet |

## LiDAR 驱动 DAG 配置

```protobuf
// modules/drivers/lidar/conf/lidar_conf.pb.txt
lidar_config {
  model: "Pandar64"           # 雷达型号
  frame_id: "velodyne128"      # TF 坐标系
  channel_name: "/apollo/sensor/lidar128/PointCloud2"
  
  // 网络配置
  config {
    ip: "192.168.1.201"        # 雷达 IP
    port: 2368                 # 数据端口
  }
  
  // 点云补偿
  compensator {
    enable: true
    imu_channel: "/apollo/sensor/gnss/imu"
  }
}
```

## 点云检测器

Apollo-lite lidar 感知模块：

```
modules/perception/lidar/
├── app/          # 点云检测主流程
└── lib/          # 算法库
    ├── object_filter/     # 地面分割/ROI过滤
    ├── roi_filter/        # 感兴趣区域过滤
    └── ...
```

### 典型点云处理流程

```cpp
// 点云处理流水线
1. PointCloud Preprocessing
   -  ROI Filter (去除车身周围地面点)
   -  Ground Segmentation (RANSAC/PlaneFit)

2. Object Detection
   -  PointPillars / CenterPoint (CNN-based)
   -  Euclidean Clustering (传统方法)

3. Object Tracking
   -  Kalman Filter + Hungarian Algorithm
   -  多帧关联
```

## 点云补偿（Motion Compensation）

LiDAR 扫描一帧需要时间（~100ms），车辆运动导致点云畸变：

```protobuf
// compensator 配置
compensator_config {
  enable: true
  
  // IMU 数据用于补偿
  imu_channel: "/apollo/sensor/gnss/imu"
  
  // 补偿方法
  method: "LINEAR_INTERPOLATION"  # 线性插值
}
```

**验证方法**：
- 静态场景：灯杆应呈直线，不倾斜
- 动态场景：同向车辆边缘应清晰，不拉伸

## 多 LiDAR 融合

```protobuf
// fusion 配置
multi_lidar_fusion_config {
  lidar_sources: "lidar_front"
  lidar_sources: "lidar_rear"
  lidar_sources: "lidar_left"
  lidar_sources: "lidar_right"
  
  // 融合策略
  fusion_method: "BOX_OVERLAP"  # 包围盒重叠
  iou_threshold: 0.5
}
```

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| 点云数据断流 | 网络丢包/雷达过热 | 检查交换机、雷达温度 |
| 地面点分割错误 | 坡度/颠簸路面 | 调整 ground_segmentation 参数 |
| 小目标漏检 | 点云稀疏 | 增加点云分辨率或使用多帧累积 |
| 动态目标拖影 | 补偿失效 | 检查 IMU 时间同步、补偿算法 |
| 多雷达融合错位 | 外参不准 | 重新标定雷达间外参 |
