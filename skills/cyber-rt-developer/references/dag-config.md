# DAG 配置规范

一句话简介：DAG（有向无环图）文件定义了 Cyber RT 中各个 Component 的依赖关系、Channel 连接以及调度策略，是系统启动的核心配置。

## 核心概念/原理

DAG 文件以 `.dag` 为后缀，本质是一个 protobuf 文本格式的配置文件。它描述了：
- 模块名称与 so 文件路径
- 组件实例及其配置
- 输入输出 Channel 绑定
- 调度优先级和资源限制

Cyber RT 在启动时会解析 DAG 文件，按拓扑顺序加载组件，确保依赖的 Channel 先有发布者后有订阅者。

## Apollo-Lite 中的实现位置

- DAG 定义文件：`modules/<module_name>/dag/<name>.dag`
- 解析器实现：`cyber/mainboard/module_argument.cc`
- 调度图构建：`cyber/scheduler/` 下的 Scheduler 实现
- 示例 DAG：`modules/perception/dag/perception.dag`

## 关键配置参数/接口

典型 DAG 配置结构：

```protobuf
module_config {
  module_library: "/apollo/bazel-bin/modules/planning/libplanning_component.so"
  components {
    class_name: "PlanningComponent"
    config {
      name: "planning"
      flag_file_path: "/apollo/modules/planning/conf/planning.conf"
      readers {
        channel: "/apollo/prediction"
        qos_profile {
          depth: 10
        }
      }
      writers {
        channel: "/apollo/planning"
      }
    }
  }
}
```

关键字段：
- `module_library`：so 文件的绝对路径或相对于工作目录的路径
- `class_name`：Component 的类名，必须与注册名一致
- `name`：组件实例名，用于日志标识
- `readers/writers`：输入输出 Channel 绑定
- `qos_profile`：Reader 的 QoS 配置

## 常见问题与排查

**Q: 启动时报 "module_library not found"？**
- 确认 so 文件路径正确，建议使用绝对路径或 `$(APOLLO_PATH)` 变量
- 检查是否已编译目标模块（`bazel build //modules/...`）

**Q: Channel 连接不上？**
- DAG 中的 `channel` 名称必须全局唯一且与代码中一致
- 注意 `readers` 和 `writers` 的层级关系，不要写错缩进

**Q: 组件加载顺序问题？**
- Cyber RT 会自动按 DAG 依赖拓扑排序加载，无需手动指定顺序
- 循环依赖会导致启动失败，需重构组件拆分

## 与其他模块的接口关系

- **Scheduler**：DAG 中的资源限制配置会直接传递给 Scheduler
- **Channel QoS**：Reader 配置中的 `qos_profile` 会传递给底层 Transport 层
- **Component**：DAG 是 Component 的实例化配置，与 Component 代码一一对应
