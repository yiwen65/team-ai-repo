# Cyber RT 服务发现机制

一句话简介：Service Discovery 负责维护 Cyber RT 集群中所有 Node、Channel、Service 的实时拓扑信息，使各模块能够自动发现彼此并建立通信连接。

## 核心概念/原理

Cyber RT 的服务发现基于 DDS 的 Discovery 机制，结合自定义扩展：

- **TopologyManager**：全局拓扑管理器，维护所有参与者（Participant）的状态
- **NodeManager**：管理 Node 的生命周期和属性
- **ChannelManager**：管理 Channel 的发布/订阅关系
- **ServiceManager**：管理 RPC 服务的注册与发现

发现流程：
1. Node 启动时向 TopologyManager 注册自身属性
2. Writer 创建时广播 Channel 发布信息
3. Reader 创建时查询匹配的 Writer 并建立连接
4. 拓扑变更（节点上下线）通过回调通知所有监听者

## Apollo-Lite 中的实现位置

- 拓扑管理：`cyber/service_discovery/topology_manager.h`
- 节点管理：`cyber/service_discovery/node_manager.h`
- Channel 管理：`cyber/service_discovery/channel_manager.h`
- 服务管理：`cyber/service_discovery/service_manager.h`
- 变更通知：`cyber/proto/topology_change.proto`

## 关键接口

```cpp
// 监听拓扑变更
topology_manager_->AddTopologyCallback([](const ChangeMsg& msg) {
  if (msg.change_type() == ChangeType::NODE_LEAVE) {
    AWARN << "Node left: " << msg.node_name();
  }
});
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| Reader 收不到消息 | Writer 未被发现 | `cyber_node info` 检查 Writer 是否注册 |
| 节点掉线未感知 | 心跳超时 | 检查 `heartbeat_timeout_ms` 配置 |
| 拓扑信息不一致 | 网络分区 | 检查各主机间的 DDS 发现端口连通性 |
| 节点重复注册 | 节点名称冲突 | 确保不同实例使用唯一 `node_name` |

## 与其他模块的接口

- **Transport**：Service Discovery 为 Transport 提供对端地址，是通信的前提
- **Scheduler**：拓扑变更可能触发调度策略调整
- **Monitor**：拓扑异常（节点大量掉线）会上报到 Monitor
