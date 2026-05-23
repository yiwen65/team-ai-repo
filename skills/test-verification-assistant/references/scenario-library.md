# 场景库设计参考

## 场景分层模型（PEGASUS / SAJ）

```
功能场景 (Functional Scenario)
  └── 逻辑场景 (Logical Scenario)  [参数化]
       └── 具体场景 (Concrete Scenario)  [确定参数]
            └── 测试用例 (Test Case)
                 └── 仿真/实车执行
```

## 功能场景分类

| 大类 | 子类 | 典型场景 |
|------|------|---------|
| 基础驾驶 | 车道保持、变道、跟车 | 直道行驶、弯道行驶、超车 |
| 交叉口 | 直行、左转、右转 | 无保护左转、闯红灯预警 |
| 泊车 | 垂直、平行、斜列 | 窄车位泊车、跨车位泊车 |
| 特殊道路 | 环岛、匝道、 toll | 匝道汇流、环岛绕行 |
| VRU | 行人、骑车人、动物 | 鬼探头、闯红灯行人 |
| 恶劣天气 | 雨、雪、雾、强光 | 雨天刹车距离、雪天车道线 |
| 异常场景 | 施工、事故、 fallback | 施工借道、异形障碍物 |

## ODD（设计运行域）定义

```yaml
ODD:
  road_type: [urban, highway, parking]
  speed_range: [0, 120]  # km/h
  weather: [clear, light_rain, light_snow]
  lighting: [day, dusk, night_with_streetlight]
  traffic: [light, moderate]
  special: [no_construction, no_severe_weather]
```

**超出 ODD 的处理**：
- 可预测：提前减速、请求接管
- 突然：紧急制动 + 安全停车

## 场景参数化

逻辑场景通过参数分布定义：

```python
# 无保护左转场景参数
scenario_params = {
    "ego_speed": {"dist": "uniform", "range": [20, 40]},  # km/h
    "oncoming_distance": {"dist": "uniform", "range": [30, 100]},  # m
    "oncoming_speed": {"dist": "uniform", "range": [30, 60]},  # km/h
    "gap_acceptance": {"dist": "binary", "p": 0.3},  # 是否接受间隙
    "pedestrian_present": {"dist": "binary", "p": 0.1}
}
```

## 覆盖度度量

| 层级 | 度量方法 | 目标 |
|------|---------|------|
| 功能场景 | 检查表 | 100% 覆盖 |
| 逻辑场景 | 参数空间采样 | > 80% 参数组合 |
| 具体场景 | 数量 | > 10000 条/功能 |
| 测试用例 | 执行通过率 | > 95% |
