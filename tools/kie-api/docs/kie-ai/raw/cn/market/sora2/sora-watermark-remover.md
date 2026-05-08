# Sora2 水印移除

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
      summary: Sora2 水印移除
      deprecated: false
      description: >-
        ## 查询任务状态


        提交任务后，可通过统一的查询端点查看任务进度并获取生成结果：


        <Card title="Get Task Details" icon="lucide-search"
        href="/cn/market/common/get-task-detail">
          了解如何查询任务状态并获取生成结果
        </Card>


        ::: tip[]

        生产环境中，建议使用 `callBackUrl` 参数接收生成完成的自动通知，而非轮询状态端点。

        :::


        ## 相关资源


        <CardGroup cols={2}>
          <Card title="Market Overview" icon="lucide-store" href="/cn/market/quickstart">
            浏览所有可用模型
          </Card>
          <Card title="Common API" icon="lucide-cog" href="/cn/common-api/get-account-credits">
            查看账户积分与使用情况
          </Card>
        </CardGroup>
      operationId: sora-watermark-remover
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
                    - sora-watermark-remover
                  default: sora-watermark-remover
                  description: |-
                    用于处理任务的模型名称。必填字段。

                    - 该端点必须使用 `sora-watermark-remover` 模型
                  examples:
                    - sora-watermark-remover
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    接收去水印任务完成通知的回调 URL。可选配置，建议在生产环境中使用。


                    - 任务处理完成后，系统会向该 URL POST 任务状态与结果

                    - 回调内容包含处理后视频的 URL 与任务相关信息

                    - 您的回调端点需要支持接收带 JSON 负载的 POST 请求

                    - 也可以选择调用任务详情端点，主动轮询任务状态

                    - 为确保回调安全性，请参阅 [Webhook
                    校验指南](/cn/common-api/webhook-verification) 了解签名验证实现方法
                  examples:
                    - https://your-domain.com/api/callback
                input:
                  type: object
                  description: 去水印任务的输入参数
                  properties:
                    video_url:
                      description: >-
                        输入 Sora 2 生成的视频 URL — 必须是 OpenAI 提供的可公开访问链接（以
                        sora.chatgpt.com 开头）。（最大长度：500 字符）
                      type: string
                      maxLength: 500
                      examples:
                        - >-
                          https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f
                    upload_method:
                      type: string
                      description: 上传目标存储。默认为 s3；选择 oss 使用阿里云存储（在中国大陆访问更优）。
                      enum:
                        - s3
                        - oss
                      x-apidog-enum:
                        - value: s3
                          name: ''
                          description: ''
                        - value: oss
                          name: ''
                          description: ''
                  required:
                    - video_url
                    - upload_method
                  x-apidog-orders:
                    - video_url
                    - upload_method
                    - 01KMCX33BB89HA8W85TG2ND56A
                    - 01KJ78H7D5F80MRQ6VTZ8X6135
                  x-apidog-refs:
                    01KJ78H7D5F80MRQ6VTZ8X6135:
                      type: object
                      properties: {}
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-watermark-remover
              callBackUrl: https://your-domain.com/api/callback
              input:
                video_url: https://sora.chatgpt.com/p/s_68e83bd7eee88191be79d2ba7158516f
                upload_method: s3
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
                  taskId: task_sora-watermark-remover_1765183831860
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506688-run
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
