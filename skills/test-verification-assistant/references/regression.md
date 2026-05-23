# 回归验证参考

## A/B 测试

**目的**：对比新旧版本在同一场景下的表现差异

**设计原则**：
1. 相同场景库、相同随机种子
2. 相同评估指标、相同通过标准
3. 统计显著性：样本量 > 1000 场景，置信度 > 95%

**对比维度**：
| 维度 | 指标 |
|------|------|
| 安全性 | 碰撞率、脱离率、AEB 触发率 |
| 效率 | 通行时间、平均速度 |
| 舒适性 | jerk、横向加速度 |
| 可用性 | 规划成功率、系统可用率 |

## 影子模式（Shadow Mode）

**原理**：
- 新版本在后台运行，不控制车辆
- 对比新旧版本输出差异
- 当差异 > 阈值时触发告警

**触发条件**：
- 规划轨迹偏差 > 1m
- 控制输出差异 > 10%
- 决策不一致（刹车 vs 加速）

**用途**：
- 大规模验证（数十万 km 无风险）
- 发现边缘场景问题
- 收集训练数据（新旧模型差异样本）

## 最小回归测试集

**选择策略**：
1. 变更影响分析：代码 diff → 受影响模块 → 关联场景
2. 历史高脱离场景：优先覆盖
3. 边界场景：不遗漏
4. P0 用例：100% 覆盖

**自动化集成**：
```yaml
# CI 流水线
regression_pipeline:
  trigger: [PR to main, nightly]
  steps:
    - code_diff_analysis
    - test_selection
    - sil_execution: {parallel: 100, timeout: 30min}
    - result_comparison
    - pass_criteria: {collision_rate: 0, disengagement_rate: < baseline}
```
