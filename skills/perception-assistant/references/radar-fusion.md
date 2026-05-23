# Apollo Radar 融合参考

## 支持的毫米波雷达

Apollo-lite drivers/radar 支持：

| 品牌 | 型号 | 探测距离 | 角度精度 | 用途 |
|------|------|---------|---------|------|
| Continental | ARS430/ARS540 | 300m | 1.5° | 前向主雷达 |
| NanoRadar | NSR100W | 100m | 3° | 角雷达 |
| Racobit | RB-24GHz | 50m | 10° | 低速/泊车 |
| Udas | UMR-24GHz | 30m | 15° | 超声波替代 |

## Radar 输出特性

```protobuf
// ContiRadar 消息结构
ContiRadarObs {
  double longitude_dist;   # 纵向距离 (m)
  double lateral_dist;     # 横向距离 (m)
  double longitude_vel;    # 纵向速度 (m/s)
  double lateral_vel;      # 横向速度 (m/s)
  double rcs;              # 雷达散射截面 (dBsm)
  
  // 目标属性
  int32 obstacle_class;    # 0=点, 1=车, 2=卡车, 3=行人, 4=摩托, 5=自行车, 6=宽车
  int32 meas_state;        # 测量状态
  int32 prob_of_exist;     # 存在概率
}
```

## Radar-Camera 融合

Apollo-lite 感知融合策略：

```
Radar Detection (目标级) + Camera Detection (目标级)
  → Association (数据关联)
  → Fusion (属性融合)
  → Output (融合目标)
```

### 关联算法

```cpp
// 基于位置和速度的关联
bool Associate(const RadarObject& radar, const CameraObject& camera) {
  // 位置差
  double pos_diff = sqrt(pow(radar.x - camera.x, 2) + 
                         pow(radar.y - camera.y, 2));
  
  // 速度差
  double vel_diff = abs(radar.vx - camera.vx);
  
  // 关联门限
  return pos_diff < 2.0 && vel_diff < 3.0;
}
```

### 属性融合规则

| 属性 | 来源优先级 | 说明 |
|------|-----------|------|
| 位置 | Camera > Radar | 相机横向精度高 |
| 速度 | Radar > Camera | 雷达速度测量直接 |
| 类别 | Camera > Radar | 相机分类能力强 |
| 存在概率 | max(Radar, Camera) | 取高置信度 |

## Radar 特有优势

1. **全天候**: 雨雾天气性能优于 Camera/LiDAR
2. **速度直接测量**: 基于多普勒效应，不依赖帧差
3. **远距离**: 前向雷达可达 300m

## 常见问题

| 问题 | 根因 | 修复 |
|------|------|------|
| 虚警多 | 金属护栏/井盖反射 | 增加 RCS 过滤、静态杂波抑制 |
| 角度精度差 | 雷达固有分辨率限制 | 结合 Camera 修正横向位置 |
| 行人漏检 | 行人 RCS 小 | 降低检测阈值（可能增加虚警） |
| 隧道失效 | 多径效应 | 结合 LiDAR/Camera 冗余 |
| 静止目标丢失 | 雷达滤波器抑制 | 调整静态目标保留策略 |
