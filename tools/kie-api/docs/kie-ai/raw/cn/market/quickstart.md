# Market

> 通过统一的 API 探索并集成尖端的 AI 模型，包括图像生成、视频制作和音频处理。

## 欢迎来到 Market

通过我们的统一 API 平台访问全面的尖端 AI 模型。从最新的图像生成、视频制作和音频模型中选择，以增强您的应用程序。

## 图像模型

用于图像生成、编辑和增强的全面 AI 模型集合。

<CardGroup cols={3}>
  <Card title="Seedream" icon="lucide-image" href="/cn/market/seedream/seedream-v3">
    具有独特艺术风格的创意图像生成 (v4.0, v4.5)
  </Card>

  <Card title="Grok Imagine" icon="lucide-image" href="/cn/market/grok-imagine/text-to-image">
    由 Grok AI 驱动的高质量照片级图像生成、文本生成图像和放大
  </Card>

  <Card title="Flux-2" icon="lucide-image" href="/cn/market/flux2/flex-text-to-image">
    先进的文本生成图像和图像到图像生成
  </Card>

  <Card
    title="Google Imagen"
    icon="lucide-image"
    href="/cn/market/google/imagen4-fast"
  >
    尖端的图像生成 (Imagen4 Fast/Ultra)
  </Card>

  <Card title="Ideogram" icon="lucide-image" href="/cn/market/ideogram/v3-reframe">
    具有角色一致性的创意图像生成
  </Card>

  <Card title="Qwen" icon="lucide-image" href="/cn/market/qwen/text-to-image">
    多语言图像生成和编辑
  </Card>

  <Card title="Recraft" icon="lucide-image" href="/cn/market/recraft/crisp-upscale">
    专业图像放大和背景移除
  </Card>

  <Card title="Topaz" icon="lucide-image" href="/cn/market/topaz/image-upscale">
    AI 驱动的图像增强和放大
  </Card>
</CardGroup>

## 视频模型

从文本和图像进行视频创建、编辑和转换的高级 AI 模型。

<CardGroup cols={3}>
  <Card title="Kling" icon="lucide-video" href="/cn/market/kling/v2-1-pro">
    高质量视频生成和 AI 头像 (v2.1, v2.5)
  </Card>

  <Card title="Sora2" icon="lucide-video" href="/cn/market/sora2/sora-2-pro-text-to-video">
    从文本和图像进行尖端视频生成
  </Card>

  <Card title="Bytedance" icon="lucide-video" href="/cn/market/bytedance/v1-pro-text-to-video">
    快速高效的视频生成 (v1 Pro/Lite)
  </Card>

  <Card title="Hailuo" icon="lucide-video" href="/cn/market/hailuo/2-3-image-to-video-pro">
    具有多种风格的高质量视频生成
  </Card>

  <Card title="Wan" icon="lucide-video" href="/cn/market/wan/2-2-a14b-text-to-video-turbo">
    具有涡轮性能的高级视频生成
  </Card>

  <Card title="Grok Imagine Video" icon="lucide-video" href="/cn/market/grok-imagine/text-to-video">
    从文本和图像生成视频
  </Card>
</CardGroup>

## 音频模型

包括语音合成、识别和效果的 AI 驱动音频处理。

<CardGroup cols={2}>
  <Card title="ElevenLabs" icon="lucide-music" href="/cn/market/elevenlabs/text-to-speech-turbo-2-5">
    高质量文本转语音、语音转文本和音频隔离
  </Card>
</CardGroup>

## 聊天模型

用于自然语言理解和生成的高级对话式 AI 模型。

<CardGroup cols={2}>
  <Card title="Gemini 2.5 Flash" icon="lucide-message-square-more" href="/cn/market/gemini/gemini-2-5-flash">
    低延迟聊天完成，支持按需推理与结构化输出
  </Card>

  <Card title="Gemini 2.5 Pro" icon="lucide-message-square-more" href="/cn/market/gemini/gemini-2-5-pro">
    面向复杂提示的高级推理与长上下文对话
  </Card>
</CardGroup>

## 开始使用

<Steps>
  <Step title="选择您的模型">
    从上面的类别中选择最适合您的用例的 AI 模型。
  </Step>

  <Step title="获取 API Key">
    访问 [API Key 管理页面](https://kie.ai/api-key) 获取您的 API 凭据。
  </Step>

  <Step title="集成">
    按照模型特定的文档将 API 集成到您的应用程序中。
  </Step>

  <Step title="开始创建">
    通过简单的 API 调用，使用您选择的 AI 模型开始生成内容。
  </Step>
</Steps>

## 身份验证

市场中的所有模型都使用相同的身份验证方法：

```bash  theme={null}
Authorization: Bearer YOUR_API_KEY
```

<Warning>
  保持您的 API key 安全。永远不要在客户端代码或公共仓库中暴露它。
</Warning>

## 统一的 API 结构

所有模型都遵循一致的 API 结构以便于集成：

### 创建任务

```bash  theme={null}
POST https://api.kie.ai/api/v1/jobs/createTask
```

### 查询任务状态

```bash  theme={null}
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}
```

### 回调通知

可选的 webhook 回调会在任务完成时通知您，无需轮询。

<Tip>
  每个模型都有独特的参数和功能。请参考各个模型文档以获取详细规范。
</Tip>

## 积分和定价

不同模型根据其计算要求消耗不同的积分数量：

* **图像模型**：每次生成通常消耗 10-50 积分
* **视频模型**：每次生成通常消耗 100-500 积分
* **语言模型**：按 token 使用量收费

查看您的剩余积分：

```bash  theme={null}
GET https://api.kie.ai/api/v1/chat/credit
```

## 支持

需要帮助选择合适的模型或集成我们的 API？

* 邮箱：[support@kie.ai](mailto:support@kie.ai)
* 文档：在导航中浏览模型特定的指南
* 社区：加入我们的 Discord 服务器进行讨论和更新

