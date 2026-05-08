# 创建音乐视频

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/mp4/generate:
    post:
      summary: 创建音乐视频
      deprecated: false
      description: |-
        基于您生成的音乐曲目创建带有可视化效果的视频。

        ### 使用指南
        - 使用此接口将您的音频曲目转换为视觉吸引力强的视频
        - 为您的音乐视频添加艺术家署名和品牌标识
        - 视频可以在社交媒体上分享或嵌入网站

        ### 参数详情
        - `taskId` 标识原始音乐生成任务
        - `audioId` 在存在多个变体时指定要可视化的音频曲目
        - 可选的 `author` 和 `domainName` 为视频添加自定义品牌

        ### 开发者注意事项
        - 生成的视频文件保留14天
        - 视频针对社交媒体分享进行了优化
        - 处理时间因音频长度和服务器负载而异
      operationId: create-music-video
      tags:
        - docs/zh-CN/Market/Suno API/Music Video Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: 音乐生成任务的唯一标识符。应为"生成音乐"或"延长音乐"接口返回的taskId。
                  examples:
                    - taskId_774b9aa0422f
                audioId:
                  type: string
                  description: 要可视化的特定音频曲目的唯一标识符。此ID在音乐生成完成后的回调数据中返回。
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    用于接收音乐视频生成任务完成更新的URL地址。所有音乐视频生成请求都需要此参数。


                    - 系统将在音乐视频生成完成时向此URL发送POST请求，包含任务状态和结果

                    - 回调包含生成的音乐视频文件URL，包含视觉效果和品牌标识

                    - 您的回调端点应能接受包含视频文件位置的JSON载荷的POST请求

                    - 详细的回调格式和实现指南，请参见
                    [音乐视频生成回调](/cn/suno-api/create-music-video-callbacks)

                    - 或者，您也可以使用获取音乐视频详情接口来轮询任务状态

                    - 为确保回调安全性，请参阅 [Webhook
                    校验指南](/cn/common-api/webhook-verification) 了解签名验证实现方法
                  examples:
                    - https://api.example.com/callback
                author:
                  type: string
                  maxLength: 50
                  description: 要在视频封面上显示的艺术家或创作者姓名。最多50个字符。这为音乐创作者创建署名。
                  examples:
                    - 电子音乐DJ
                domainName:
                  type: string
                  maxLength: 50
                  description: 要在视频底部显示为水印的网站或品牌。最多50个字符。适用于促销品牌或归属。
                  examples:
                    - music.example.com
              x-apidog-orders:
                - taskId
                - audioId
                - callBackUrl
                - author
                - domainName
              x-apidog-ignore-properties: []
            example:
              taskId: taskId_774b9aa0422f
              audioId: e231****-****-****-****-****8cadc7dc
              callBackUrl: https://api.example.com/callback
              author: DJ Electronic
              domainName: music.example.com
      responses:
        '200':
          description: 成功
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
                          - 409
                          - 422
                          - 429
                          - 455
                          - 500
                        description: |-
                          响应状态码

                          - **200**: 成功 - 请求已成功处理
                          - **400**: 格式错误 - 参数不是有效的JSON格式
                          - **401**: 未授权 - 身份验证凭据缺失或无效
                          - **402**: 积分不足 - 账户没有足够的积分执行此操作
                          - **404**: 未找到 - 请求的资源或端点不存在
                          - **409**: 冲突 - WAV记录已存在
                          - **422**: 验证错误 - 请求参数未通过验证检查
                          - **429**: 超出限制 - 您的调用频率过高。请稍后再试。
                          - **455**: 服务不可用 - 系统当前正在进行维护
                          - **500**: 服务器错误 - 处理请求时发生意外错误
                          构建失败 - 音频MP4生成失败
                      msg:
                        type: string
                        description: 当 code != 200 时的错误信息
                        examples:
                          - success
                    x-apidog-orders:
                      - code
                      - msg
                    x-apidog-ignore-properties: []
                type: object
                properties:
                  code:
                    type: integer
                    format: int32
                    description: 状态码
                    examples:
                      - 0
                  msg:
                    type: string
                    description: 状态信息
                    examples:
                      - ''
                  data:
                    type: object
                    properties:
                      taskId:
                        type: string
                        description: 任务id
                        examples:
                          - ''
                    x-apidog-orders:
                      - taskId
                    x-apidog-ignore-properties: []
                x-apidog-orders:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 0
                msg: ''
                data:
                  taskId: ''
          headers: {}
          x-apidog-name: ''
        '500':
          description: 请求失败
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apidog-orders: []
                x-apidog-ignore-properties: []
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
        onMp4Generated:
          '{$request.body#/callBackUrl}':
            post:
              summary: MP4生成完成回调
              description: 当MP4生成完成后，系统会向提供的回调URL发送POST请求通知结果
              requestBody:
                required: true
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
                                - 500
                              description: |-
                                响应状态码

                                - **200**: 成功 - 请求已成功处理
                                - **500**: 内部错误 - 请稍后再试。
                            msg:
                              type: string
                              description: 当 code != 200 时的错误信息
                              example: success
                      type: object
                      required:
                        - code
                        - msg
                        - data
                      properties:
                        code:
                          type: integer
                          description: 状态码，0表示成功
                          example: 0
                        msg:
                          type: string
                          description: 状态信息
                          example: msg_9a23a47664f7
                        data:
                          type: object
                          required:
                            - task_id
                            - video_url
                          properties:
                            task_id:
                              type: string
                              description: 生成任务的唯一标识符
                              example: task_id_5bbe7721119d
                            video_url:
                              type: string
                              description: 可访问的视频URL，有效期14天
                              example: video_url_847715e66259
              responses:
                '200':
                  description: 回调接收成功
      x-apidog-folder: docs/zh-CN/Market/Suno API/Music Video Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506737-run
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
