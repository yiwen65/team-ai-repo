# 局部轨迹参考

## Frenet 坐标系

Frenet 坐标系以参考线（reference line）为基准：
- `s`：沿参考线纵向距离
- `l`：偏离参考线的横向距离
- 优势：将 2D 问题解耦为纵向 + 横向独立优化

## 典型轨迹生成器

### EM Planner（Apollo）

**流程**：
1. 路径规划（Path）：在 `l-s` 空间采样，优化横向偏移
2. 速度规划（Speed）：在 `s-t` 空间采样，优化纵向速度
3. 评估器（Evaluator）：障碍物、交通规则、舒适性打分
4. 最优组合：path + speed 最优配对

**关键参数**：
```yaml
path_evaluator:
  lattice_num: 5  # 横向采样数
  lattice_width: 0.5  # 采样间隔 (m)
  
speed_evaluator:
  time_resolution: 0.1  # 时间分辨率 (s)
  num_time_steps: 50  # 预测步数
  
constraint:
  max_lateral_acceleration: 2.0  # m/s²
  max_longitudinal_jerk: 2.5  # m/s³
```

### Lattice Planner

**适用**：结构化道路（高速、快速路）
**采样**：横向偏移 + 纵向速度/加速度组合
**代价函数**：平滑性 + 障碍物 + 车道保持 + 舒适性

### OpenSpace Planner

**适用**：泊车、窄路掉头、非结构化场景
**方法**：
1. Hybrid A*：粗搜索（Reeds-Shepp 曲线）
2. 凸优化（IPOPT/OSQP）：平滑优化
3. 分舵角轨迹：满足车辆运动学

## 轨迹质量检查清单

- [ ] 曲率连续性（无突变）
- [ ] 加速度在约束范围内
- [ ] 无碰撞（与静态/动态障碍物）
- [ ] 满足交通规则（车道线、信号灯）
- [ ] 舒适性（jerk、横向加速度）
- [ ] 末端状态可达（与下周期衔接）
