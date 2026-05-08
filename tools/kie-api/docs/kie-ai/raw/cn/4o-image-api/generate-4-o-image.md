# 生成4o图像

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/gpt4o-image/generate:
    post:
      summary: 生成4o图像
      deprecated: false
      description: 创建一个新的4o图像生成任务。生成的图片保存14天，14天后过期。
      operationId: generate-4o-image
      tags:
        - docs/zh-CN/Market/Image    Models/4o Image API
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                fileUrl:
                  type: string
                  format: uri
                  description: >-
                    （可选，即将废弃）文件URL，例如图片的URL。如果提供fileUrl，4o
                    image可能会基于该图片进行创作。该参数将在未来被废弃，请使用filesUrl替代。
                  deprecated: true
                  examples:
                    - https://example.com/image.png
                maskUrl:
                  type: string
                  format: uri
                  description: >-
                    （可选）蒙版图片URL。你可以提供一个蒙版（mask）来指示图像应该在哪些区域进行编辑。蒙版中黑色的部分将被替换或修改，其他区域使用白色填充。你可以使用文字描述你希望最终编辑后的图像是什么样子，或者具体想要修改哪些内容。蒙版图片必须与编辑的图片具有相同的格式和尺寸（小于25MB）。当filesUrl包含超过1张图片时，此参数不可用。蒙版图片的尺寸必须与filesUrl中的图片保持一致。


                    示例：

                    ![蒙版示例](https://static.aiquickdraw.com/images/docs/4o-gen-image-mask.png)


                    上图中，左侧是原始图片，中间是蒙版图片（白色区域表示要保留的部分，黑色区域表示要修改的部分），右侧是最终生成的图片。
                  examples:
                    - https://example.com/mask.png
                filesUrl:
                  type: array
                  items:
                    type: string
                    format: uri
                  description: >-
                    （可选）文件URL列表，例如图片URL列表。最多支持5张图片。支持的文件格式：`.jfif`、`.pjpeg`、`.jpeg`、`.pjp`、`.jpg`、`.png`、`.webp`
                  examples:
                    - - https://example.com/image1.png
                      - https://example.com/image2.jpg
                prompt:
                  type: string
                  description: （可选）提示词，用于描述你希望4o image生成的内容。fileUrl/filesUrl和prompt至少需要提供一个
                  examples:
                    - A beautiful sunset over the mountains
                size:
                  type: string
                  description: （必填）图片尺寸比例，必须是支持的格式之一
                  enum:
                    - '1:1'
                    - '3:2'
                    - '2:3'
                  examples:
                    - '1:1'
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    用于接收4o图像生成任务完成更新的URL地址。可选但推荐在生产环境中使用。


                    - 系统将在4o图像生成完成时向此URL发送POST请求，包含任务状态和结果

                    - 回调包含生成的图像URL和任务信息，支持所有变体

                    - 您的回调端点应能接受包含图像生成结果的JSON载荷的POST请求

                    - 详细的回调格式和实现指南，请参见
                    [4o图像生成回调](https://docs.kie.ai/cn/4o-image-api/generate-4-o-image-callbacks)

                    - 或者，您也可以使用获取4o图像详情接口来轮询任务状态

                    - 为确保回调安全性，请参阅 [Webhook
                    校验指南](/cn/common-api/webhook-verification) 了解签名验证实现方法
                  examples:
                    - https://your-callback-url.com/callback
                isEnhance:
                  type: boolean
                  description: >-
                    （可选）提示增强选项，默认值为 false。在大多数情况下，启用此功能是不必要的。但是，对于生成 3D
                    图像等特定场景，启用它可以产生更精细的效果。谨慎使用。
                  examples:
                    - false
                uploadCn:
                  type: boolean
                  description: >-
                    （可选）指定图片上传的服务器区域。设置为 true 时使用中国大陆服务器，false
                    时使用海外服务器。可根据您的地理位置选择最优的上传节点以获得更好的上传速度。
                  examples:
                    - false
                enableFallback:
                  type: boolean
                  description: >-
                    （可选）是否启用托底机制。当设置为 true 时，如果官方 GPT-4o
                    图像生成服务不可用或出现异常，系统将自动切换到备用模型（如 Flux
                    等）进行图像生成，以确保任务的连续性和可靠性。默认值为 false。
                  examples:
                    - false
                fallbackModel:
                  type: string
                  description: >-
                    （可选）指定托底模型。当 enableFallback 为 true
                    时生效，用于选择在主模型不可用时使用哪个备用模型来生成图片。可选值：GPT_IMAGE_1 或
                    FLUX_MAX。默认值为 FLUX_MAX。
                  enum:
                    - GPT_IMAGE_1
                    - FLUX_MAX
                  default: FLUX_MAX
                  examples:
                    - FLUX_MAX
              required:
                - size
              x-apidog-orders:
                - fileUrl
                - maskUrl
                - filesUrl
                - prompt
                - size
                - callBackUrl
                - isEnhance
                - uploadCn
                - enableFallback
                - fallbackModel
              examples:
                - filesUrl:
                    - https://example.com/image1.png
                    - https://example.com/image2.png
                  prompt: A beautiful sunset over the mountains
                  size: '1:1'
                  callBackUrl: https://your-callback-url.com/callback
                  isEnhance: false
                  uploadCn: false
                  enableFallback: false
                  fallbackModel: FLUX_MAX
              x-apidog-ignore-properties: []
            example:
              filesUrl:
                - https://example.com/image.png
              prompt: A beautiful sunset over the mountains
              size: '1:1'
              callBackUrl: https://your-callback-url.com/callback
              isEnhance: false
              uploadCn: false
              enableFallback: false
              fallbackModel: FLUX_MAX
      responses:
        '200':
          description: 请求成功
          content:
            application/json:
              schema:
                allOf:
                  - type: object
                    properties:
                      code:
                        type: integer
                        enum:
                          - 200
                          - 400
                          - 401
                          - 402
                          - 404
                          - 422
                          - 429
                          - 455
                          - 500
                          - 550
                        description: |-
                          响应状态码

                          - **200**: 成功 - 请求已成功处理  
                          - **400**: 格式错误 - 参数不是有效的 JSON 格式  
                          - **401**: 未授权 - 缺少身份验证凭据或凭据无效  
                          - **402**: 积分不足 - 账户没有足够的积分执行此操作  
                          - **404**: 未找到 - 请求的资源或端点不存在  
                          - **422**: 参数错误 - 请求参数未通过验证检查  
                          - **429**: 超出限制 - 已超过对此资源的请求限制  
                          - **455**: 服务不可用 - 系统当前正在进行维护  
                          - **500**: 服务器错误 - 在处理请求时发生意外错误  
                            - 构建失败 - 人声移除生成失败  
                          - **550**: 连接被拒绝 - 任务因队列已满而被拒绝，可能是由于源站点问题导致。请联系管理员确认。
                      msg:
                        type: string
                        description: 当 code != 200 时的错误信息
                        examples:
                          - success
                    x-apidog-orders:
                      - code
                      - msg
                    x-apidog-ignore-properties: []
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: >-
                              任务id，可使用
                              [获取4o图像详情](/zh-CN/4o-image-api/get-4-o-image-details)
                              查询任务状态
                            examples:
                              - task12345
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
                  taskId: task12345
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
      callbacks:
        on4oImageGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: 4o Image生成任务回调
              description: 当4o Image任务完成后，系统会向您提供的回调URL发送POST请求通知结果
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: |-
                            状态码

                            - **200**: 成功 - 图片生成完成  
                            - **400**: 参数错误  
                              - filesUrl 参数中的图片内容违反内容政策  
                              - 图片尺寸超过最大限制 26214400 字节  
                              - 无法处理提供的图片文件（代码 = invalid_image_format）  
                              - 您的内容被 OpenAI 标记为违反内容政策  
                            - **451**: 下载失败 - 无法从提供的 filesUrl 下载图片  
                            - **500**: 服务器错误  
                              - 请稍后重试  
                              - 获取用户令牌失败  
                              - 生成图片失败  
                              - GPT 4O 编辑图片失败  
                              - null
                          enum:
                            - 200
                            - 400
                            - 451
                            - 500
                        msg:
                          type: string
                          description: 状态信息
                          example: success
                        data:
                          type: object
                          properties:
                            taskId:
                              type: string
                              description: 任务ID
                              example: task12345
                            info:
                              type: object
                              properties:
                                result_urls:
                                  type: array
                                  items:
                                    type: string
                                  description: 生成的图片URL列表
                                  example:
                                    - https://example.com/result/image1.png
                    example:
                      code: 200
                      msg: success
                      data:
                        taskId: task12345
                        info:
                          result_urls:
                            - https://example.com/result/image1.png
              responses:
                '200':
                  description: 回调接收成功
      x-apidog-folder: docs/zh-CN/Market/Image    Models/4o Image API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506739-run
components:
  schemas: {}
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
