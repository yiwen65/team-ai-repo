# Apollo Camera 感知参考

## 检测器架构

Apollo-lite camera 感知采用流水线架构：

```
DataProvider (图像预处理)
  → ObstacleDetector (YOLO/DarkSCNN) / LaneDetector (DarkSCNN/DenseLine) / TrafficLightDetector
  → ObjectTransformer (2D→3D)
  → Tracker (OMT/ByteTrack)
  → Output
```

## YOLO 检测器配置

```protobuf
// modules/perception/camera/lib/obstacle/detector/yolo/yolo_obstacle_detector.conf
yolo_obstacle_detector_config {
  model_param {
    model_name: "yolo-3d"
    proto_file: "yolo-3d.prototxt"
    weight_file: "yolo-3d.caffemodel"
    input_blob: "data"
    output_blob: "prob"
    input_width: 960
    input_height: 384
  }
  
  // NMS 参数
  nms_param {
    type: "IoU"
    threshold: 0.5
  }
  
  // 类别映射
  obj_map: "car"
  obj_map: "pedestrian"
  obj_map: "cyclist"
  obj_map: "truck"
}
```

## 车道线检测器对比

| 检测器 | 网络结构 | 速度 | 精度 | 适用 |
|--------|---------|------|------|------|
| DarkSCNN | SCNN (Spatial CNN) | 30ms | 高 | 结构化道路 |
| DenseLine | 密集采样回归 | 20ms | 中 | 简单场景 |

## 红绿灯检测

```protobuf
// traffic_light_detection.conf
traffic_light_detection_config {
  model_param {
    model_name: "traffic_light"
    proto_file: "traffic_light.prototxt"
    weight_file: "traffic_light.caffemodel"
  }
  
  // 检测区域（从地图获取信号灯位置投影）
  projection_param {
    boundary_distance: 5.0  # 米
  }
  
  // 识别参数
  recognition_param {
    threshold: 0.7
  }
}
```

## 相机标定验证

```bash
# 运行相机标定验证工具
/apollo/bazel-bin/modules/perception/camera/tools/offline/offline_obstacle_pipeline \
  --config_path=/apollo/modules/perception/camera/conf/camera_obstacle_detection.conf
```

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| 检测器输出全 0 | 模型未加载/输入尺寸不匹配 | 检查 model_param 配置 |
| 车道线断裂 | SCNN 消息传递不足 | 调整 spatial_loss_weight |
| 红绿灯漏检 | 投影位置偏移 | 检查相机-地图外参 |
| OMT 跟踪 ID 跳变 | 遮挡/相似目标 | 调大 min_hits，降低 max_age |
| 2D→3D 位置偏移 | 相机内参/外参错误 | 重新标定，检查 ground_plane |

## OMT 跟踪器参数

```protobuf
omt_obstacle_tracker_config {
  min_hits: 3           # 新目标确认帧数
  max_age: 5            # 丢失后保留帧数
  iou_threshold: 0.3    # 关联阈值
  
  // 外观特征
  feature_param {
    use_deep_feature: true
    feature_dim: 128
  }
}
```
