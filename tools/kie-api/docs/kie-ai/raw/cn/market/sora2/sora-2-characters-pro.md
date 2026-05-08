# Sora2 - Characters Pro

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
      summary: Sora2 - Characters Pro
      deprecated: false
      description: >-
        创建动态角色动画，使用 Sora-2-characters-pro 高级 AI 模型从现有视频任务中提取角色。


        ## 前置条件


        Sora-2-characters-pro API 从**现有视频生成任务**中生成角色动画。在使用此 API 之前，您必须有一个已完成的任务：


        1. **完成视频生成任务**

           首先，使用 Sora 视频生成 API（例如 [Text to Video](/cn/market/sora2/sora-2-text-to-video) 或 [Image to Video](/cn/market/sora2/sora-2-image-to-video)）创建一个视频。

        2. **获取任务 ID**

           视频生成成功完成后，从响应中记下 `taskId`。这将成为您的 `origin_task_id`。

        3. **指定视频片段**

           使用 `timestamps` 参数定义要使用视频的哪个片段。格式：`"x,y"`（例如 `"3.55,5.55"`）。片段持续时间（y - x）必须在 1-4 秒之间。

        4. **提交角色动画任务**

           提供 `origin_task_id`、`timestamps` 和 `character_prompt` 以生成角色动画。可选地包含 `character_user_name` 以标识角色供后续引用。

        ## 参数参考


        | 参数 | 类型 | 必填 | 描述 |

        |:---|:---|:---|:---|

        | `origin_task_id` | string | 是 | 原始视频生成任务的任务 ID |

        | `timestamps` | string | 是 | 视频片段时间范围。格式：`"x,y"`（例如 `"3.55,5.55"`）。从 x
        到 y 秒提取片段。持续时间（y - x）必须为 1-4 秒 |

        | `character_user_name` | string | 否 | 可选。角色的自定义名称，用于在后续操作中标识和引用。提供时最多
        40 个字符 |

        | `character_prompt` | string | 是 | 描述角色个性和外观的角色人设提示词 |

        | `safety_instruction` | string | 否 | 动画的安全指南和内容限制 |


        :::caution 时间戳限制


        `timestamps` 参数必须定义 1-4 秒的片段。例如，`"3.55,5.55"` 提取一个 2
        秒的片段。无效的持续时间将导致处理错误。


        :::


        :::tip[]


        在提交角色动画请求之前，使用 [Get Task Details](/cn/market/common/get-task-detail)
        端点验证您的原始视频任务已成功完成。


        :::


        ## 查询任务状态


        提交任务后，使用统一查询端点检查进度并检索结果：


        [Get Task Details](/cn/market/common/get-task-detail)


        了解如何查询任务状态和检索生成结果。


        ### 任务查询响应格式


        当任务成功完成时（`state: "success"`），`resultJson` 字段包含：


        ```json

        {
          "character_id": "example_123456789"
        }

        ```


        `character_id` 可用于在后续操作中引用生成的角色动画。


        :::tip[]


        对于生产环境使用，我们建议使用 `callBackUrl` 参数在生成完成时接收自动通知，而不是轮询状态端点。


        :::


        ## 相关资源


        - [Market Overview](/cn/market/quickstart) - 探索所有可用模型

        - [Common API](/cn/common-api/get-account-credits) - 检查积分和账户使用情况
      operationId: sora-2-characters-pro
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
                    - sora-2-characters-pro
                  default: sora-2-characters-pro
                  description: |-
                    要使用的模型名称。必需字段。

                    - 此端点必须为 `sora-2-characters-pro`
                  examples:
                    - sora-2-characters-pro
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
                    origin_task_id:
                      type: string
                      description: 原先任务的 task_id。引用之前已完成的视频生成任务。
                      examples:
                        - 7118f712c1f35c9b8bf2ad1af68ad482
                    timestamps:
                      type: string
                      description: >-
                        请输入视频片段的开始和结束时间（以秒为单位）。您选择的片段必须完全包含在原始视频中，且长度在 1 秒到 4
                        秒之间；该片段将用作角色的训练素材。
                      examples:
                        - 3.55,5.55
                    character_user_name:
                      type: string
                      description: 可选。角色的自定义名称，用于在后续操作中标识和引用该角色。若提供则需非空且最大 40 字符。
                      maxLength: 40
                      examples:
                        - my_character_01
                    character_prompt:
                      type: string
                      description: 角色人设提示词。必填，非空。描述角色的个性和外观。
                      maxLength: 5000
                      examples:
                        - 一个友好的卡通角色，有着富有表现力的眼睛和流畅的动作
                    safety_instruction:
                      type: string
                      description: 角色安全指令。动画的安全指南和内容限制。
                      maxLength: 5000
                      examples:
                        - 确保动画适合家庭观看，不包含暴力或不适当的内容
                  required:
                    - origin_task_id
                    - timestamps
                    - character_prompt
                  x-apidog-orders:
                    - origin_task_id
                    - timestamps
                    - character_user_name
                    - character_prompt
                    - safety_instruction
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-2-characters-pro
              callBackUrl: https://your-domain.com/api/callback
              input:
                origin_task_id: 7118f712c1f35c9b8bf2ad1af68ad482
                timestamps: 3.55,5.55
                character_user_name: my_character_01
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
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: 任务 ID，可用于获取任务详情端点查询任务状态
                            examples:
                              - 7118f712c1f35c9b8bf2ad1af68ad482
                        x-apidog-orders:
                          - taskId
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  taskId: task_sora-2-characters-pro_1765174270120
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28563260-run
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
