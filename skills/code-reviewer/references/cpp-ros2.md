# C++ ROS2 代码审查参考

## 实时性规范

**硬实时线程禁止**：
- ❌ `malloc` / `free` / `new` / `delete`
- ❌ 文件 I/O（`fopen`, `printf`, `std::cout`）
- ❌ 网络 I/O（阻塞 socket）
- ❌ 动态库加载（`dlopen`）
- ❌ 锁（`std::mutex::lock`，应使用无锁或实时锁）

**推荐**：
- ✅ 预分配内存池（`std::array`, `boost::pool`）
- ✅ 无锁队列（`boost::lockfree::spsc_queue`）
- ✅ 实时锁（`pthread_mutex` + `PTHREAD_PRIO_INHERIT`）

## ROS2 节点设计规范

```cpp
// 推荐：节点构造函数只做初始化，业务逻辑在回调中
class PerceptionNode : public rclcpp::Node {
public:
    explicit PerceptionNode(const rclcpp::NodeOptions &options)
        : Node("perception_node", options) {
        // 参数声明
        declare_parameter("model_path", "model.onnx");
        
        // QoS 配置
        rclcpp::QoS qos(10);
        qos.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);
        qos.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
        
        // 订阅
        sub_ = create_subscription<sensor_msgs::msg::Image>(
            "/camera/front/image_raw", qos,
            std::bind(&PerceptionNode::onImage, this, std::placeholders::_1));
    }
    
private:
    void onImage(const sensor_msgs::msg::Image::SharedPtr msg) {
        // 处理逻辑
    }
    
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

## 话题命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 传感器原始数据 | `/sensor/<type>/<location>/raw` | `/sensor/camera/front/image_raw` |
| 处理后数据 | `/perception/<module>/output` | `/perception/detection/3d_objects` |
| 控制指令 | `/control/<lateral\|longitudinal>/cmd` | `/control/longitudinal/brake_cmd` |
| 诊断信息 | `/diagnostics/<module>` | `/diagnostics/perception/fps` |

## 常见安全问题

| 问题 | 示例 | 修复 |
|------|------|------|
| 裸指针 | `cv::Mat* ptr = new cv::Mat()` | `cv::Mat ptr;` 或 `std::unique_ptr` |
| 越界访问 | `data[idx]` 未检查 idx | `if (idx < size) data[idx]` |
| 资源泄漏 | `FILE* f = fopen(...)` 无 fclose | RAII 封装或 `std::fstream` |
| 竞态条件 | 多线程读写共享变量 | `std::atomic` 或互斥锁 |
| 死锁 | 双锁嵌套顺序不一致 | 统一加锁顺序或使用 `std::lock` |

## 性能要点

- **避免 `sensor_msgs::PointCloud2` 拷贝**：使用 `std::move` 或指针传递
- **Eigen 固定大小矩阵**：`Eigen::Matrix4f` 比 `Eigen::MatrixXf` 快 10x
- **向量化**：编译选项 `-mavx2 -mfma`，循环内无数据依赖
- **缓存友好**：点云处理按顺序访问，`std::vector` 连续存储
