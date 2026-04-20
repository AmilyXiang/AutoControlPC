# DECT 与 AutoControlPC 整合方案

## 目标

把目前独立的两套能力合并为一套统一测试框架：

- 由 `AutoControlPC/run_testcase.py` 作为唯一入口执行整体 case
- 保留 `AutoControlPC` 现有的 `keyboard`、`mouse`、`ocr`、`audio`、`network` 等步骤能力
- 把 `dect` 的机械按键、串口控制、相机抓图、YOLO/PaddleOCR 校验纳入同一套 testcase 中
- 支持一个 testcase 里混合执行 `dect`、`audio`、桌面自动化等步骤

## 推荐原则

推荐采用“单一编排器 + 设备适配层”的方式，而不是继续维护两个独立主程序。

核心原则如下：

- `AutoControlPC` 负责 testcase 解析、步骤调度、日志、异常终止、资源生命周期
- `dect` 不再保留自己的主执行循环，只保留可复用的设备能力模块
- testcase 继续以 XML 为主，优先做最小增量扩展，避免一次性推翻现有 case 体系
- 每一种能力都以独立 step handler 形式接入，后续新增 `audio`、`process`、`network`、`dect` 时不会互相耦合

## 不推荐的方案

### 方案 A：把 `dect/src/main.py` 直接嵌到 `run_testcase.py`

不推荐。原因：

- `dect/src/main.py` 当前是无限循环模型，不适合作为 testcase step 执行单元
- 串口、相机、识别器初始化和释放逻辑混在主流程里，难以与现有 runner 协同
- 后面加 `audio`、`network`、PC UI 自动化时，会继续堆在一个大 `if/elif` 里

### 方案 B：继续维护两套 testcase，再互相调用

也不推荐。原因：

- 用例会被拆成两种格式，维护成本高
- 跨系统步骤的时序和失败处理会变复杂
- 日志、报告、重试、资源回收都无法统一

## 推荐架构

### 1. 保留一个统一入口

保留 `AutoControlPC/run_testcase.py` 作为总入口。

它负责：

- 解析 XML
- 创建执行上下文
- 按顺序执行 step
- 统一日志输出
- 遇错立即停止 testcase
- 在 testcase 结束时统一释放资源

### 2. 引入执行上下文 `ExecutionContext`

新增一个上下文对象，供所有 step handler 共享资源。

建议包含：

- `ocr_tool`
- `network`
- `audio_state`
- `dect_session`
- `variables`
- `logger`

其中 `dect_session` 应该延迟初始化，只有遇到 `type="dect"` 的 step 时才创建。

### 3. 把 step 执行改成 handler 注册表

不要继续把所有逻辑堆在一个超长 `if/elif` 中。建议改成：

```python
STEP_HANDLERS = {
    'keyboard': execute_keyboard_step,
    'mouse': execute_mouse_step,
    'audio': execute_audio_step,
    'network': execute_network_step,
    'ocr': execute_ocr_step,
    'icon': execute_icon_step,
    'dect': execute_dect_step,
}
```

这样做的好处：

- 新增类型时只需要增加一个 handler
- `dect` 逻辑可以独立维护
- 便于后续做单元测试

### 4. 把 DECT 抽成适配层

建议把 `dect` 里的能力拆成下面几个类，再由 `AutoControlPC` 调用。

#### `DectController`

负责机械按键和串口交互：

- 初始化串口
- 初始化机械臂/移动接口
- `press_key(key_name)`
- `long_press_key(key_name)`
- `move_to_key(key_name)`
- `origin()`
- `close()`

这个类内部封装：

- `moveserial.SerialInterface`
- `move.MoveInterface`
- `KeyLayout`

#### `DectVision`

负责图像抓取和识别：

- 初始化相机
- 初始化 YOLO/PaddleOCR 分析器
- `capture()`
- `detect()`
- `assert_text(text, timeout=...)`
- `assert_icon(name, timeout=...)`
- `close()`

这个类内部封装：

- `getImage.CameraGrabber`
- `Analyze_icon_text`
- `cut_image.straighten_screen_from_np`

#### `DectSession`

负责把控制和视觉组合起来，给 testcase 使用：

- `press(...)`
- `assert_text(...)`
- `assert_icon(...)`
- `cleanup()`

### 5. XML 增加 `dect` step 类型

推荐在现有 XML 格式上最小扩展，不要新造第二种 testcase 格式。

建议先支持下面几类 step：

#### 按键步骤

```xml
<step type="dect" action="press" key="1" />
<step type="dect" action="press" key="hangup" post_delay="2" />
<step type="dect" action="press" key="hangoff" pre_delay="4" post_delay="2" />
```

#### 按键并校验文本

```xml
<step type="dect" action="press" key="hangup" post_delay="2" expect_text="Calling" />
```

#### 单独校验文本

```xml
<step type="dect" action="assert_text" content="Call ended" timeout="5" />
```

#### 单独校验图标

```xml
<step type="dect" action="assert_icon" content="signal" timeout="5" />
```

#### 回原点

```xml
<step type="dect" action="origin" />
```

### 6. 保留 layout 与 testcase 的职责边界

推荐把按键坐标 layout 和 testcase 分离。

- testcase 只描述“按哪个键、等多久、期望看到什么”
- layout 单独保存在一个配置文件中，例如 `dect_layout.json` 或专门的 Python 配置模块

不建议把 layout 直接写进 XML。因为 layout 属于设备标定数据，不属于测试流程。

## 从现有 `sequence.py` 到 XML 的映射方式

现有结构：

```python
[key, delay_before_press, delay_after_press, expected_response]
```

建议映射关系：

- `key` -> `key`
- `delay_before_press` -> `pre_delay`
- `delay_after_press` -> `post_delay`
- `expected_response['text']` -> `expect_text`
- `expected_response` 中非 `text` 的图标键 -> `expect_icon`

例如：

```python
['hangup', 0, 2, {"sig": None, "text": "Calling"}]
```

映射为：

```xml
<step type="dect" action="press" key="hangup" post_delay="2" expect_text="Calling" expect_icon="sig" />
```

如果 `sig: None` 只是占位而不是实际校验项，则不要输出 `expect_icon`。

## 推荐的目录调整

建议最终把与 DECT 相关、但要被总执行器调用的代码移动或镜像到 `AutoControlPC` 目录下，形成统一项目结构。

例如：

```text
AutoControlPC/
  run_testcase.py
  step_handlers/
    keyboard_steps.py
    mouse_steps.py
    audio_steps.py
    dect_steps.py
  integrations/
    dect/
      controller.py
      vision.py
      session.py
      layout.py
  testcase/
    dect_call.xml
    mixed_call_audio.xml
```
```

这样做的原因：

- `AutoControlPC` 变成唯一可发布项目
- import 路径更稳定
- 避免两个顶层项目互相引用时出现路径和环境问题

## 推荐的 testcase 写法

### 纯 DECT case

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <testcase name="DECT_Call">
        <step type="dect" action="press" key="1" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="hangup" post_delay="2" expect_text="Calling" />
        <step type="dect" action="press" key="hangoff" pre_delay="4" post_delay="2" expect_text="Call ended" />
        <step type="dect" action="origin" />
    </testcase>
</testcases>
```

### 混合 DECT + Audio case

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testcases>
    <testcase name="DECT_Call_With_Audio">
        <step type="dect" action="press" key="1" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="0" />
        <step type="dect" action="press" key="hangup" post_delay="2" expect_text="Calling" />
        <step type="audio" action="play_async" content="testAudioFile/sine_40.wav" device="headset" time="5" />
        <step type="wait" action="sleep" content="5" />
        <step type="dect" action="press" key="hangoff" expect_text="Call ended" />
        <step type="audio" action="stop_record" />
        <step type="dect" action="origin" />
    </testcase>
</testcases>
```

## 失败处理建议

统一执行器里建议采用以下策略：

- 任一步骤失败立即抛异常并停止当前 testcase
- testcase 结束时必须执行 `cleanup`
- `dect` 资源释放失败不能吞掉日志
- 对识别类步骤加入超时重试，而不是只抓一帧就判失败

例如：

- `assert_text(timeout=5, interval=0.5)`
- 在 5 秒内循环抓图识别
- 超时后抛出明确异常

## 识别步骤的实现建议

相比当前 `sequence.py` 中“按一次键就抓一帧”的方式，更推荐：

- 按键完成后进入轮询识别
- 在超时时间内连续抓图
- 只要检测到期望文本或 icon 即成功

这样比单帧识别更稳定。

## 资源生命周期建议

推荐按 testcase 维度管理资源：

- 首次遇到 `dect` step 时初始化 `DectSession`
- 后续 `dect` step 复用同一个 session
- testcase 结束后统一调用 `cleanup`

不要每个 `dect` step 都重新初始化串口、相机和模型，否则性能和稳定性都会变差。

## 实施顺序

### 第一阶段

目标：先跑通最小链路。

- 把 `dect` 的串口控制和图像识别封装成可 import 的类
- 在 `run_testcase.py` 里新增 `dect` step handler
- 支持 `press`、`assert_text`、`origin`
- 手工写一个最小 XML case 跑通

### 第二阶段

目标：完成从 `sequence.py` 到 XML 的迁移。

- 把现有 `sequence.py` 中的 sequence 转成 XML testcase
- layout 保留为配置文件
- 增加 `expect_icon`、`timeout`、`retry_interval`

### 第三阶段

目标：增强混合场景。

- 在一个 testcase 中混合 `dect`、`audio`、`network`
- 增加公共变量和上下文传值能力
- 增加 testcase 级 setup/teardown

## 最终建议

如果目标是长期维护并继续扩展，推荐你采用下面这条路线：

1. 以 `AutoControlPC` 为唯一总执行器
2. 把 `dect` 重构为一个被调用的设备适配层，而不是独立主程序
3. 在现有 XML step 体系中新增 `dect` 类型，而不是再造一套 testcase 格式
4. 把 layout 和 testcase 分离
5. 先做最小闭环，再逐步把旧 `sequence.py` 迁移掉

这是当前代码基础上改动成本最低、后续扩展性最好的一种方案。