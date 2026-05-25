# 相对地图（RelativeMap）

一句话简介：RelativeMap 是 Apollo-Lite 基于实时感知和定位生成的局部地图，在 HDMap 不可用或精度不足时提供车道线、边界和导航路径的相对表示，支持 Planning 模块继续工作。

## 核心概念/原理

RelativeMap 生成流程：
1. **定位输入**：当前车辆在 HDMap 中的位姿（来自 Localization）
2. **感知输入**：相机检测的车道线、障碍物边界
3. **融合生成**：将感知结果投影到车辆局部坐标系，生成相对车道线
4. **导航路径**：基于 Routing 结果生成局部导航路径

关键特点：
- 局部有效（通常前方 50-200m）
- 实时更新（与感知同频）
- 不依赖全局高精地图完整性

## Apollo-Lite 中的实现位置

- RelativeMap：`modules/world_model/relative_map/`
- 导航路径：`modules/world_model/relative_map/navigation_lane.cc/.h`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 相对地图为空 | 感知车道线检测失败 | 检查 camera perception 输出 |
| 导航路径偏移 | localization 漂移 | 对比 localization 和 GPS 位置 |
| 车道线断裂 | 感知模型在特定场景失效 | 增加隧道/夜间训练数据 |

## 与其他模块的接口

- **perception/camera**：车道线检测输入
- **localization**：车辆全局位姿
- **planning**：使用 RelativeMap 替代 HDMap 进行规划
- **routing**：提供导航路径参考
