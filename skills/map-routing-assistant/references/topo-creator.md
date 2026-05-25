# 拓扑图生成（TopoCreator）

一句话简介：TopoCreator 将 HDMap 的车道几何和连接关系转换为 Routing 可用的拓扑图（节点=车道，边=连接关系），是 Routing 引擎运行前的必要预处理步骤。

## 核心概念/原理

拓扑图构建流程：
1. **车道节点化**：每条 Lane 创建一个节点，包含长度、限速、类型
2. **连接边化**：Lane 的 successor/predecessor/left/right 创建有向边
3. **权重计算**：边权重 = 长度 / 平均速度 + 转弯惩罚
4. **索引优化**：空间索引加速起点/终点的最近车道查找

输出格式：
- 二进制拓扑图文件（.bin），供 Routing 模块加载

## Apollo-Lite 中的实现位置

- 拓扑生成：`modules/routing/topo_creator/`
- 图结构：`modules/routing/graph/`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 拓扑图缺失连接 | HDMap junction 定义不完整 | 检查 junction 的 connection |
| 节点属性错误 | 限速/长度解析错误 | 对比 HDMap 原始值 |
| 空间索引失效 | 坐标系转换错误 | 检查 ENU/UTM 转换参数 |

## 与其他模块的接口

- **map/hdmap**：输入来源
- **routing/core**：消费拓扑图进行路径搜索
