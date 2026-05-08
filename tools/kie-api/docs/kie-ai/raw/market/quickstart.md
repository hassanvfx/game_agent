# Market

> Explore and integrate cutting-edge AI models for image generation, video creation, and audio processing through unified APIs.

## Welcome to the Market

Access a comprehensive collection of state-of-the-art AI models through our unified API platform. Choose from the latest image generation, video creation, and audio models to power your applications.

## Image Models

Comprehensive collection of AI models for image generation, editing, and enhancement.

<CardGroup cols={3}>
  <Card title="Z-image" icon="lucide-image" href="/market/z-image/z-image">
    Creative image generation with unique artistic styles (v4.0, v4.5)
  </Card>

  <Card title="Grok Imagine" icon="lucide-image" href="/market/grok-imagine/text-to-image">
    High-quality photorealistic images, text-to-image, and upscaling
  </Card>

  <Card title="Flux-2" icon="lucide-image" href="/market/flux2/pro-text-to-image">
    Advanced text-to-image and image-to-image generation
  </Card>

  <Card title="Google Imagen" icon="lucide-image" href="/market/google/imagen4">
    State-of-the-art image generation (Imagen4 Fast/Ultra)
  </Card>

  <Card title="Ideogram" icon="lucide-image" href="/market/ideogram/character">
    Creative image generation with character consistency
  </Card>

  <Card title="Qwen" icon="lucide-image" href="/market/qwen/text-to-image">
    Multilingual image generation and editing
  </Card>

  <Card title="Recraft" icon="lucide-image" href="/market/recraft/crisp-upscale">
    Professional image upscaling and background removal
  </Card>

  <Card title="Topaz" icon="lucide-image" href="/market/topaz/image-upscale">
    AI-powered image enhancement and upscaling
  </Card>
</CardGroup>

## Video Models

Advanced AI models for video creation, editing, and transformation from text and images.

<CardGroup cols={3}>
  <Card title="Kling" icon="lucide-video" href="/market/kling/v2-1-pro">
    High-quality video generation and AI avatars (v2.1, v2.5)
  </Card>

  <Card title="Sora2" icon="lucide-video" href="/market/sora2/sora-2-pro-text-to-video">
    State-of-the-art video generation from text and images
  </Card>

  <Card title="Bytedance" icon="lucide-video" href="/market/bytedance/v1-pro-text-to-video">
    Fast and efficient video generation (v1 Pro/Lite)
  </Card>

  <Card title="Hailuo" icon="lucide-video" href="/market/hailuo/2-3-image-to-video-pro">
    High-quality video generation with multiple styles
  </Card>

  <Card title="Wan" icon="lucide-video" href="/market/wan/2-6-image-to-video">
    Advanced video generation with turbo performance
  </Card>

  <Card title="Grok Imagine Video" icon="lucide-video" href="/market/grok-imagine/text-to-video">
    Video generation from text and images
  </Card>
</CardGroup>

## Audio Models

AI-powered audio processing including speech synthesis, recognition, and effects.

<CardGroup cols={2}>
  <Card title="ElevenLabs" icon="lucide-music" href="/market/elevenlabs/text-to-speech-turbo-2-5">
    High-quality text-to-speech, speech-to-text, and audio isolation
  </Card>
</CardGroup>

## Chat Models

Advanced conversational AI models for natural language understanding and generation.

<CardGroup cols={2}>
  <Card title="Gemini 2.5 Flash" icon="lucide-message-square-more" href="/market/gemini/gemini-2-5-flash">
    Fast chat completions with optional reasoning and structured outputs
  </Card>

  <Card title="Gemini 2.5 Pro" icon="lucide-message-square-more" href="/market/gemini/gemini-2-5-pro">
    Advanced reasoning and long-context chat for complex prompts
  </Card>
</CardGroup>

## Getting Started

<Steps>
  <Step title="Choose Your Model">
    Select the AI model that best fits your use case from the categories above.
  </Step>

  <Step title="Get API Key">
    Visit the [API Key Management Page](https://kie.ai/api-key) to obtain your API credentials.
  </Step>

  <Step title="Integrate">
    Follow the model-specific documentation to integrate the API into your application.
  </Step>

  <Step title="Start Creating">
    Begin generating content using your chosen AI model through simple API calls.
  </Step>
</Steps>

## Authentication

All models in the market use the same authentication method:

```bash  theme={null}
Authorization: Bearer YOUR_API_KEY
```

:::warning[Security Requirement]
Keep your **API Key** strictly confidential.
 **Never expose it** in client-side code (browsers, mobile apps) or public repositories (like GitHub).
:::

## Unified API Structure

All models follow a consistent API structure for ease of integration:

### Create Task

```bash  theme={null}
POST https://api.kie.ai/api/v1/jobs/createTask
```

### Query Task Status

```bash  theme={null}
GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}
```

### Callback Notifications

Optional webhook callbacks notify you when tasks complete, eliminating the need for polling.

:::tip[]
  Each model has unique parameters and capabilities. Refer to individual model documentation for detailed specifications.
:::

## Credits and Pricing

Different models consume different amounts of credits based on their computational requirements:

* **Image Models**: Typically 10-50 credits per generation
* **Video Models**: Typically 100-500 credits per generation
* **Language Models**: Charged per token usage

Check your remaining credits:

```bash  theme={null}
GET https://api.kie.ai/api/v1/chat/credit
```

## Support

Need help choosing the right model or integrating our APIs?

* Email: [support@kie.ai](mailto:support@kie.ai)
* Documentation: Browse model-specific guides in the navigation
* Community: Join our Discord server for discussions and updates

