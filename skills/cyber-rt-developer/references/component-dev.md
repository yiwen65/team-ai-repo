# Cyber RT Component 开发指南

一句话简介：Cyber RT Component 是 Apollo-Lite 中实现模块化、异步通信的基础单元，每个 Component 通过 Reader/Writer 进行数据交换。

## 核心概念/原理

Cyber RT 采用基于 DAG（有向无环图）的组件化架构。每个 Component 是一个独立的计算单元，通过声明式的输入输出 Channel 进行数据通信。Component 的生命周期由 Cyber 框架管理，包括 Init、Proc 和 Clear 三个阶段。

关键设计原则：
- **无共享状态**：组件间不直接共享内存，通过 Channel 传递 protobuf 消息
- **零拷贝传输**：同一进程内使用 Intra 传输，共享内存使用 SHM，跨进程使用 RTPS
- **自动调度**：根据 DAG 依赖关系自动触发组件执行

## Apollo-Lite 中的实现位置

- 基类定义：`cyber/component/component.h`
- 示例组件：`modules/perception/onboard/component/` 下的各类感知组件
- DAG 加载器：`cyber/mainboard/module_argument.cc`
- Component 注册宏：`CYBER_REGISTER_COMPONENT`

## 关键配置参数/接口

```cpp
class MyComponent : public Component<MyMsgType> {
 public:
  bool Init() override;
  bool Proc(const std::shared_ptr<MyMsgType>& msg) override;
};
```

关键接口：
- `bool Init()`：初始化组件，创建 Reader/Writer
- `bool Proc()`：主处理逻辑，由数据到达触发
- `template <typename T> bool GetProtoConfig(T* config)`：读取私有配置文件

## 常见问题与排查

**Q: Component 启动后没有收到数据？**
- 检查 DAG 中 Channel 名称是否与发布端一致（区分大小写）
- 使用 `cyber_channel info /channel/name` 查看是否有发布者
- 确认 Component 的 Reader 和 Writer 模板类型与消息类型匹配

**Q: Proc 函数没有被调用？**
- 检查 DAG 配置中 `freq` 字段是否正确
- 如果是 TimerComponent，检查定时器是否触发
- 查看日志中的 `Init` 返回值，若为 false 则不会进入 Proc

**Q: 内存泄漏或消息堆积？**
- Reader 默认队列深度为 10，可通过 `reader->SetHistoryDepth()` 调整
- 确保 Proc 处理速度高于数据到达速度，否则需限流或异步处理

## 与其他模块的接口关系

- **Scheduler**：Component 的执行由 Scheduler 统一调度，配置在 `cyber/conf/` 下
- **Record**：Component 的输入输出可通过 cyber_recorder 录制和回放
- **Parameter Server**：Component 可通过参数服务动态调整配置
- **Transport**：底层依赖 RTPS/SHM/Intra 三种传输机制
