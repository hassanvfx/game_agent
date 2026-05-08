# Sora2 - Characters

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
      summary: Sora2 - Characters
      deprecated: false
      description: >
        ## 文件上传要求


        在使用角色动画 API 之前，您需要上传角色视频：


        <Steps>
          <Step title="上传角色视频">
            访问我们的[文件上传 API](/cn/file-upload-api/upload-file-url) 来上传您的角色视频。

            **要求：**
            - **文件类型**：MP4、WebM 或 AVI 格式
            - **持续时间**：每个视频 1-4 秒之间
            - **最大文件大小**：每个文件 10MB
            - **内容**：您想要制作动画的角色动作或动作

            每个动画任务只能上传一个角色视频。
          </Step>

          <Step title="获取上传 URL">
            成功上传后，您将收到可用于 `character_file_url` 参数的文件 URL。
          </Step>

          <Step title="提交动画任务">
            在您的 API 请求中使用获得的 URL 来生成角色动画。
          </Step>
        </Steps>


        ## 附加参数


        除了角色视频 URL 之外，您还可以提供附加参数来增强您的角色动画：


        - **`character_prompt`**：角色描述和期望的动画风格（最多 5000 个字符）

        - **`safety_instruction`**：动画的安全指南和内容限制（最多 5000 个字符）


        这两个参数都是可选的，但建议使用以更好地控制动画输出。


        ::: warning[]

        **文件存储提醒**：通过我们的文件上传 API 上传的文件仅临时存储 14 天。在此期限后，角色 URL 将变得无效，并在使用角色动画 API
        时导致错误。我们建议使用第三方永久存储解决方案（如 AWS S3、Google Cloud Storage
        或其他云存储服务）来确保您的角色视频文件的长期可用性。

        :::


        ::: tip[]

        确保您的角色视频时长在 1-4 秒之间。超出此持续时间的视频可能会导致处理错误。

        :::


        ## 查询任务状态


        提交任务后，使用统一查询端点来检查进度并检索结果：


        <Card title="获取任务详情" icon="lucide-search"
        href="/cn/market/common/get-task-detail">
          了解如何查询任务状态并检索生成结果
        </Card>


        ### 查询任务详情响应格式


        任务成功完成时（`state: "success"`），`resultJson` 字段包含：


        ```json

        {
          "character_id": "example_123456789"
        }

        ```


        `character_id` 可用于在后续操作中引用生成的角色动画。


        ::: tip[]

        对于生产环境，我们建议使用 `callBackUrl` 参数来接收生成完成时的自动通知，而不是轮询状态端点。

        :::


        ## 相关资源


        <CardGroup cols={2}>
          <Card title="市场概览" icon="lucide-store" href="/cn/market/quickstart">
            探索所有可用模型
          </Card>
          <Card title="文件上传 API" icon="lucide-upload" href="/cn/file-upload-api/upload-file-url">
            了解如何上传您的角色视频
          </Card>
          <Card title="通用 API" icon="lucide-cog" href="/cn/common-api/get-account-credits">
            检查积分和账户使用情况
          </Card>
        </CardGroup>
      operationId: sora-2-characters
      tags:
        - docs/zh-CN/Market/Video Models/Sora2
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - model
              properties:
                model:
                  type: string
                  enum:
                    - sora-2-characters
                  default: sora-2-characters
                  description: |-
                    要使用的模型名称。必需字段。

                    - 此端点必须为 `sora-2-characters`
                  examples:
                    - sora-2-characters
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    用于接收生成任务完成更新的 URL。可选但推荐用于生产环境。


                    - 系统将在生成完成时向此 URL POST 任务状态和结果

                    - 回调包含生成的内容 URL 和任务信息

                    - 您的回调端点应接受带有 JSON 负载的 POST 请求

                    - 或者，使用获取任务详情端点来轮询任务状态

                    - 为确保回调安全性，请参阅 [Webhook
                    校验指南](/cn/common-api/webhook-verification) 了解签名验证实现方法
                  examples:
                    - https://your-domain.com/api/callback
                input:
                  type: object
                  description: 生成任务的输入参数
                  properties:
                    character_file_url:
                      description: >-
                        用于角色动画输入的角色视频 URL 数组。只允许一个视频 URL。每个视频的持续时间必须在 1-4
                        秒之间。（上传后的文件 URL，不是文件内容；接受的类型：video/mp4, video/webm,
                        video/avi；每个文件最大大小：10.0MB；持续时间：1-4 秒）
                      type: array
                      items:
                        type: string
                        format: uri
                      minItems: 1
                      maxItems: 1
                      examples:
                        - - >-
                            https://static.aiquickdraw.com/tools/example/character1.mp4
                    character_prompt:
                      description: 角色描述和期望的动画风格（最大长度：5000 个字符）
                      type: string
                      maxLength: 5000
                      examples:
                        - 一个友好的卡通角色，有着富有表现力的眼睛和流畅的动作
                    safety_instruction:
                      description: 动画的安全指南和内容限制（最大长度：5000 个字符）
                      type: string
                      maxLength: 5000
                      examples:
                        - 确保动画适合家庭观看，不包含暴力或不适当的内容
                  required:
                    - character_file_url
                  x-apidog-orders:
                    - character_file_url
                    - character_prompt
                    - safety_instruction
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-2-characters
              callBackUrl: https://your-domain.com/api/callback
              input:
                character_file_url:
                  - https://static.aiquickdraw.com/tools/example/character1.mp4
                character_prompt: 一个友好的卡通角色，有着富有表现力的眼睛和流畅的动作
                safety_instruction: 确保动画适合家庭观看，不包含暴力或不适当的内容
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
                  taskId: 7118f712c1f35c9b8bf2ad1af68ad482
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
      x-apidog-folder: docs/zh-CN/Market/Video Models/Sora2
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506687-run
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
