# Sora-2 Pro Storyboard

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
      summary: Sora-2 Pro Storyboard
      deprecated: false
      description: >
        ## 查询任务状态


        提交任务后，使用统一的查询端点检查进度并获取结果：


        <Card title="获取任务详情" icon="lucide-search"
        href="/cn/market/common/get-task-detail">
          了解如何查询任务状态并获取生成结果
        </Card>


        ::: tip[]

        对于生产环境，我们建议使用 `callBackUrl` 参数接收自动通知，而不是轮询状态端点。

        :::


        ## 相关资源


        <CardGroup cols={2}>
          <Card title="市场概览" icon="lucide-store" href="/cn/market/quickstart">
            探索所有可用模型
          </Card>
          <Card title="通用API" icon="lucide-cog" href="/cn/common-api/get-account-credits">
            查看积分和账户使用情况
          </Card>
        </CardGroup>
      operationId: sora-2-pro-storyboard
      tags:
        - docs/zh-CN/Market/Video Models/Sora2
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
                    - sora-2-pro-storyboard
                  default: sora-2-pro-storyboard
                  description: |-
                    用于生成的模型名称。必填字段。

                    - 此端点必须使用 `sora-2-pro-storyboard`
                  examples:
                    - sora-2-pro-storyboard
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
                    shots:
                      description: 分镜描述数组及其持续时间。所有分镜的总时长不能超过所选的 n_frames 值。
                      type: array
                      items:
                        type: object
                        properties:
                          Scene:
                            type: string
                            description: 场景/分镜的详细描述
                            examples:
                              - >-
                                一只可爱的蓬松橘白相间的小猫戴着橘色耳机，坐在舒适的室内桌子旁，盘子里有一小块蛋糕，附近有一个玩具鱼和银色麦克风，温暖柔和的光线，电影特写，浅景深，温柔的ASMR氛围。
                          duration:
                            type: number
                            description: 此分镜的持续时间（秒）。所有分镜的总时长不能超过 n_frames。
                            minimum: 0.1
                            maximum: 15
                            examples:
                              - 7.5
                        required:
                          - Scene
                          - duration
                        x-apidog-orders:
                          - Scene
                          - duration
                        x-apidog-ignore-properties: []
                      minItems: 1
                      maxItems: 10
                      examples:
                        - - Scene: >-
                              一只可爱的蓬松橘白相间的小猫戴着橘色耳机，坐在舒适的室内桌子旁，盘子里有一小块蛋糕，附近有一个玩具鱼和银色麦克风，温暖柔和的光线，电影特写，浅景深，温柔的ASMR氛围。
                            duration: 7.5
                          - Scene: >-
                              同一只可爱的蓬松橘白相间的小猫戴着橘色耳机，在同一个舒适的室内ASMR设置中，玩具鱼和麦克风，蛋糕现在吃完了，小猫轻轻舔着嘴唇，带着满足的微笑，温暖的环境照明，电影特写，浅景深，平静而满足的心情。
                            duration: 7.5
                    n_frames:
                      description: 视频总长度
                      type: string
                      enum:
                        - '10'
                        - '15'
                        - '25'
                      default: '15'
                      examples:
                        - '15'
                    image_urls:
                      description: >-
                        上传图片文件作为API输入（上传后的文件URL，不是文件内容；接受类型：image/jpeg,
                        image/png, image/webp；最大大小：10.0MB）。限制为正好1张图片。
                      type: array
                      items:
                        type: string
                        format: uri
                      minItems: 1
                      maxItems: 1
                      examples:
                        - - >-
                            https://file.aiquickdraw.com/custom-page/akr/section-images/1760776438785hyue5ogz.png
                    aspect_ratio:
                      description: 此参数定义图片的宽高比。
                      type: string
                      enum:
                        - portrait
                        - landscape
                      default: landscape
                      examples:
                        - landscape
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
                    - n_frames
                    - upload_method
                  x-apidog-orders:
                    - shots
                    - n_frames
                    - image_urls
                    - aspect_ratio
                    - upload_method
                    - 01KJ78G57KCN6PM133A55XYAPC
                  x-apidog-refs:
                    01KJ78G57KCN6PM133A55XYAPC:
                      type: object
                      properties: {}
                  x-apidog-ignore-properties: []
              required:
                - model
                - input
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              examples:
                - model: sora-2-pro-storyboard
                  callBackUrl: https://your-domain.com/api/callback
                  input:
                    shots:
                      - Scene: >-
                          一只可爱的蓬松橘白相间的小猫戴着橘色耳机，坐在舒适的室内桌子旁，盘子里有一小块蛋糕，附近有一个玩具鱼和银色麦克风，温暖柔和的光线，电影特写，浅景深，温柔的ASMR氛围。
                        duration: 7.5
                      - Scene: >-
                          同一只可爱的蓬松橘白相间的小猫戴着橘色耳机，在同一个舒适的室内ASMR设置中，玩具鱼和麦克风，蛋糕现在吃完了，小猫轻轻舔着嘴唇，带着满足的微笑，温暖的环境照明，电影特写，浅景深，平静而满足的心情。
                        duration: 7.5
                    n_frames: '15'
                    image_urls:
                      - >-
                        https://file.aiquickdraw.com/custom-page/akr/section-images/1760776438785hyue5ogz.png
                    aspect_ratio: landscape
              x-apidog-ignore-properties: []
            example:
              model: sora-2-pro-storyboard
              callBackUrl: https://your-domain.com/api/callback
              input:
                n_frames: '15'
                image_urls:
                  - >-
                    https://file.aiquickdraw.com/custom-page/akr/section-images/1760776438785hyue5ogz.png
                aspect_ratio: landscape
                upload_method: s3
                shots:
                  - Scene: >-
                      A cute fluffy orange-and-white kitten wearing orange
                      headphones, sitting at a cozy indoor table with a small
                      slice of cake on a plate, a toy fish and a silver
                      microphone nearby, warm soft lighting, cinematic close-up,
                      shallow depth of field, gentle ASMR atmosphere.
                    duration: 7.5
                  - Scene: >-
                      The same cute fluffy orange-and-white kitten wearing
                      orange headphones, in the same cozy indoor ASMR setup with
                      the toy fish and microphone, the cake now finished, the
                      kitten gently licks its lips with a satisfied smile, warm
                      ambient lighting, cinematic close-up, shallow depth of
                      field, calm and content mood.
                    duration: 7.5
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
                  taskId: task_sora-2-pro-storyboard_1765188271139
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506686-run
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
