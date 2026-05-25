# Cyber RT 参数服务

一句话简介：Parameter Server 是 Cyber RT 的全局动态配置服务，支持运行时参数查询、修改和监听，避免重启系统即可调整模块行为。

## 核心概念/原理

Parameter Server 采用 Client-Server 架构：
- **ParameterServer**：在每个 Node 内部运行，管理该 Node 的参数命名空间
- **ParameterClient**：通过 RPC 向其他 Node 的参数服务发起读写请求
- **参数命名空间**：以 `/node_name/parameter_name` 形式组织，支持层级结构

参数类型支持：整数、浮点、字符串、布尔、Proto 消息。

## Apollo-Lite 中的实现位置

- 参数服务：`cyber/parameter/parameter_server.h`
- 参数客户端：`cyber/parameter/parameter_client.h`
- Protobuf 定义：`cyber/proto/parameter.proto`

## 关键接口

```cpp
// Server 端（在 Component Init 中）
auto param_server = node_->CreateParameterServer();
param_server->SetParameter("max_speed", 120.0);

// Client 端（跨节点访问）
auto param_client = node_->CreateParameterClient("/planning");
double max_speed = param_client->GetParameter("max_speed")->AsDouble();

// 监听参数变更
param_server->AddParameterCallback("max_speed", [](const std::shared_ptr<Parameter>& param) {
  AINFO << "max_speed changed to: " << param->AsDouble();
});
```

## 常见问题与排查

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| 参数读取失败 | 目标 Node 未启动或参数未初始化 | 确认 Node 已注册 ParameterServer |
| 参数类型不匹配 | Client 期望类型与 Server 实际类型不同 | 使用 `Type()` 检查后再转换 |
| 参数变更未触发回调 | 回调未正确注册 | 检查 `AddParameterCallback` 的调用时机 |
| 跨节点参数延迟高 | 网络拓扑复杂 | 参数变更通过 Channel 广播，检查 QoS |

## 与其他模块的接口

- **planning**：动态调整规划参数（如最大速度、安全距离）
- **control**：在线调整 MPC 权重矩阵
- **perception**：动态切换检测模型或阈值
- **Guardian**：动态修改安全监控阈值
