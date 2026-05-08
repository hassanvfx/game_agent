# ElevenLabs音效V2

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/jobs/createTask:
    post:
      summary: ElevenLabs音效V2
      deprecated: false
      description: >
        ## 查询任务状态


        提交任务后，使用统一的查询端点检查进度并获取结果：


        <Card title="获取任务详情" icon="magnifying-glass"
        href="/cn/market/common/get-task-detail">
          了解如何查询任务状态并获取生成结果
        </Card>


        ::: tip[]

        对于生产环境，我们建议使用 `callBackUrl` 参数接收自动通知，而不是轮询状态端点。

        :::


        ## 相关资源


        <CardGroup cols={3}>
          <Card title="市场概览" icon="store" href="/cn/market/quickstart">
            探索所有可用模型
          </Card>
          <Card title="文件上传API" icon="upload" href="/cn/file-upload-api/quickstart">
            了解如何上传和管理文件
          </Card>
          <Card title="通用API" icon="gear" href="/cn/common-api/get-account-credits">
            查看积分和账户使用情况
          </Card>
        </CardGroup>
      operationId: elevenlabs-sound-effect-v2
      tags:
        - docs/zh-CN/Market/Music Models/ElevenLabs
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                model:
                  type: string
                  enum:
                    - elevenlabs/sound-effect-v2
                  default: elevenlabs/sound-effect-v2
                  description: |-
                    用于生成的模型名称。必填字段。

                    - 此端点必须使用 `elevenlabs/sound-effect-v2`
                  examples:
                    - elevenlabs/sound-effect-v2
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    接收生成任务完成更新的 URL。可选但建议在生产环境中使用。


                    - 当生成完成时，系统将向此 URL POST 任务状态和结果

                    - 回调包含生成的 URL 和任务信息

                    - 您的回调端点应接受包含结果的 JSON 负载的 POST 请求

                    - 或者，使用获取任务详情端点轮询任务状态

                    - 为确保回调安全性，请参阅 [Webhook
                    校验指南](/cn/common-api/webhook-verification) 了解签名验证实现方法
                  examples:
                    - https://your-domain.com/api/callback
                input:
                  type: object
                  description: 生成任务的输入参数
                  properties:
                    text:
                      description: 描述要生成的音效的文本（最大长度：5000 个字符）
                      type: string
                      maxLength: 5000
                      examples:
                        - ''
                    loop:
                      description: 是否创建平滑循环的音效（布尔值：true/false）
                      type: boolean
                      examples:
                        - false
                    duration_seconds:
                      description: >-
                        持续时间（秒）（0.5-22）。如果为
                        None，将根据提示确定最佳持续时间（最小值：0.5，最大值：22，步长：0.1）（步长：0.1）
                      type: number
                      minimum: 0.5
                      maximum: 22
                    prompt_influence:
                      description: >-
                        遵循提示的紧密程度（0-1）。较高的值意味着较少的变化（最小值：0，最大值：1，步长：0.01）（步长：0.01）
                      type: number
                      minimum: 0
                      maximum: 1
                      default: 0.3
                      examples:
                        - 0.3
                    output_format:
                      description: 生成的音频输出格式。以 codec_sample_rate_bitrate 格式化
                      type: string
                      enum:
                        - mp3_22050_32
                        - mp3_44100_32
                        - mp3_44100_64
                        - mp3_44100_96
                        - mp3_44100_128
                        - mp3_44100_192
                        - pcm_8000
                        - pcm_16000
                        - pcm_22050
                        - pcm_24000
                        - pcm_44100
                        - pcm_48000
                        - ulaw_8000
                        - alaw_8000
                        - opus_48000_32
                        - opus_48000_64
                        - opus_48000_96
                        - opus_48000_128
                        - opus_48000_192
                      default: mp3_44100_128
                      examples:
                        - mp3_44100_128
                  required:
                    - text
                  x-apidog-orders:
                    - text
                    - loop
                    - duration_seconds
                    - prompt_influence
                    - output_format
                  x-apidog-ignore-properties: []
              required:
                - model
                - input
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: elevenlabs/sound-effect-v2
              callBackUrl: https://your-domain.com/api/callback
              input:
                text: ''
                loop: false
                prompt_influence: 0.3
                output_format: mp3_44100_128
      responses:
        '200':
          description: 请求成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
              example:
                code: 200
                msg: success
                data:
                  taskId: 281e5b0*********************f39b9
          headers: {}
          x-apidog-name: ''
      security:
        - BearerAuth: []
          x-apidog:
            schemeGroups:
              - id: kn8M4YUlc5i0A0179ezwx
                schemeIds:
                  - BearerAuth
            required: true
            use:
              id: kn8M4YUlc5i0A0179ezwx
            scopes:
              kn8M4YUlc5i0A0179ezwx:
                BearerAuth: []
      x-apidog-folder: docs/zh-CN/Market/Music Models/ElevenLabs
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506700-run
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: |-
            响应状态码
            200: 成功 - 请求已成功处理
            401: 未授权 - 缺少身份验证凭据或凭据无效
            402: 额度不足 - 账户额度不足，无法执行该操作
            404: 未找到 - 请求的资源或接口不存在
            422: 校验错误 - 请求参数未通过校验检查
            429: 请求受限 - 已超过该资源的请求频率限制
            433: 请求限额 - 子 key 使用超出限额
            455: 服务不可用 - 系统目前正在维护中
            500: 服务器错误 - 处理请求时发生了意外错误
            501: 生成失败 - 内容生成任务失败
            505: 功能禁用 - 请求的功能目前已禁用
          enum:
            - 200
            - 401
            - 402
            - 404
            - 422
            - 429
            - 433
            - 455
            - 500
            - 501
            - 505
          x-apidog-enum:
            - value: 200
              name: ''
              description: ''
            - value: 401
              name: ''
              description: ''
            - value: 402
              name: ''
              description: ''
            - value: 404
              name: ''
              description: ''
            - value: 422
              name: ''
              description: ''
            - value: 429
              name: ''
              description: ''
            - value: 433
              name: ''
              description: ''
            - value: 455
              name: ''
              description: ''
            - value: 500
              name: ''
              description: ''
            - value: 501
              name: ''
              description: ''
            - value: 505
              name: ''
              description: ''
        msg:
          type: string
          description: 响应消息，失败时的错误描述
        data:
          type: object
          properties:
            taskId:
              type: string
              description: 任务 ID 可与“获取任务详细信息”端点一起使用，以查询任务状态
          x-apidog-orders:
            - taskId
          required:
            - taskId
          x-apidog-ignore-properties: []
      x-apidog-orders:
        - code
        - msg
        - data
      required:
        - code
        - msg
        - data
      title: response not with recordId
      x-apidog-ignore-properties: []
      x-apidog-folder: ''
  securitySchemes:
    BearerAuth:
      type: bearer
      scheme: bearer
      bearerFormat: API Key
      description: |-
        所有 API 都需要通过 Bearer Token 进行身份验证。

        获取 API Key：
        1. 访问 [API Key 管理页面](https://kie.ai/api-key) 获取您的 API Key

        使用方法：
        在请求头中添加：
        Authorization: Bearer YOUR_API_KEY

        注意事项：
        - 请妥善保管您的 API Key，切勿泄露给他人
        - 若怀疑 API Key 泄露，请立即在管理页面重置
servers:
  - url: https://api.kie.ai
    description: 正式环境
security:
  - BearerAuth: []
    x-apidog:
      schemeGroups:
        - id: kn8M4YUlc5i0A0179ezwx
          schemeIds:
            - BearerAuth
      required: true
      use:
        id: kn8M4YUlc5i0A0179ezwx
      scopes:
        kn8M4YUlc5i0A0179ezwx:
          BearerAuth: []

```
