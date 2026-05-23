# 功能安全审查参考

## MISRA C++ 关键规则

| 规则 | 说明 | 示例 |
|------|------|------|
| Rule 5-0-3 | 不使用隐式类型转换 | `int x = 3.14;` → `int x = static_cast<int>(3.14);` |
| Rule 5-2-4 | 不使用的表达式应有副作用 | `x == 5;` → `if (x == 5) { ... }` |
| Rule 7-1-2 | 所有变量在首次使用前初始化 | `int x;` → `int x = 0;` |
| Rule 8-4-4 | 函数应有单一出口点 | 避免多个 `return`，用状态变量 |
| Rule 15-3-7 | 所有异常应有对应 catch | `try` 必须配 `catch` |
| Rule 17-0-3 | 不使用汇编 | 如需，封装并文档化 |

## ASIL 合规要点

**ASIL D（最高等级）**：
- 单点故障覆盖率 > 99%
- 潜伏故障覆盖率 > 90%
- 代码审查：双人审查 + 工具扫描（Coverity/Polyspace）
- 测试：需求覆盖 100%、MC/DC 覆盖 100%

**ASIL B/C**：
- 单点故障覆盖率 > 90%
- 代码审查：单人审查 + 工具扫描
- 测试：需求覆盖 100%、分支覆盖 > 80%

## 安全编码实践

```cpp
// 推荐的 ASIL D 安全模式

// 1. 防御式编程
uint32_t getSensorData(uint32_t index) {
    if (index >= MAX_SENSORS) {
        // 安全状态：返回默认值，记录错误
        logError("Invalid sensor index: %u", index);
        return DEFAULT_VALUE;
    }
    return sensor_data_[index];
}

// 2. 断言用于不可恢复错误
void criticalFunction() {
    // 前置条件检查
    assert(ptr != nullptr);  // 仅在 Debug
    if (ptr == nullptr) {
        enterSafeState();
        return;
    }
    // ...
}

// 3. 资源管理
class SafeFileHandle {
public:
    explicit SafeFileHandle(const char* path) : fd_(open(path, O_RDONLY)) {}
    ~SafeFileHandle() { if (fd_ >= 0) close(fd_); }
    // 禁止拷贝
    SafeFileHandle(const SafeFileHandle&) = delete;
    SafeFileHandle& operator=(const SafeFileHandle&) = delete;
private:
    int fd_;
};
```

## 审查工具链

| 工具 | 用途 | 集成方式 |
|------|------|---------|
| Coverity | 静态分析 | CI/CD |
| Polyspace | 运行时错误检测 | CI/CD |
| Cppcheck | 轻量静态分析 | pre-commit |
| clang-tidy | 代码规范检查 | IDE + CI |
| Valgrind | 内存检测 | 测试阶段 |
| AddressSanitizer | 运行时内存检测 | Debug 构建 |
