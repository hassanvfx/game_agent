# 获取音乐视频详情

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/mp4/record-info:
    get:
      summary: 获取音乐视频详情
      deprecated: false
      description: |-
        获取音乐视频生成任务的详细信息。

        ### 使用指南
        - 使用此接口检查视频生成任务的状态
        - 生成完成后访问视频URL
        - 跟踪处理进度和可能发生的任何错误

        ### 状态说明
        - `PENDING`: 任务等待处理中
        - `SUCCESS`: 视频生成成功完成
        - `CREATE_TASK_FAILED`: 创建视频生成任务失败
        - `GENERATE_MP4_FAILED`: 视频文件创建过程中失败

        ### 开发者注意事项
        - 视频URL仅在状态为`SUCCESS`时在响应中可用
        - 对于失败的任务提供错误代码和消息
        - 成功生成后，视频保留14天
      operationId: get-music-video-details
      tags:
        - docs/zh-CN/Market/Suno API/Music Video Generation
      parameters:
        - name: taskId
          in: query
          description: 要获取的音乐视频生成任务的唯一标识符。这是创建音乐视频生成任务时返回的taskId。
          required: true
          example: taskId_774b9aa0422f
          schema:
            type: string
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
                          - **429**: 超出限制 - 已超过对此资源的请求限制
                          - **455**: 服务不可用 - 系统当前正在进行维护
                          - **500**: 服务器错误 - 处理请求时发生意外错误
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
                        description: 任务ID
                        examples:
                          - ''
                      musicId:
                        type: string
                        description: 音乐ID
                        examples:
                          - ''
                      callbackUrl:
                        type: string
                        description: 回调URL
                        examples:
                          - ''
                      musicIndex:
                        type: integer
                        format: int32
                        description: 歌曲索引0或者1
                        examples:
                          - 0
                      completeTime:
                        type: string
                        format: date-time
                        description: 完成回调时间
                        examples:
                          - ''
                      response:
                        type: object
                        description: 完成回调结果
                        properties:
                          videoUrl:
                            type: string
                            description: 视频URL
                            examples:
                              - ''
                        x-apidog-orders:
                          - videoUrl
                        x-apidog-ignore-properties: []
                      successFlag:
                        type: string
                        description: >-
                          PENDING-等待执行 SUCCESS-成功 CREATE_TASK_FAILED-创建任务失败
                          GENERATE_MP4_FAILED-生成MP4失败
                        examples:
                          - ''
                      createTime:
                        type: string
                        format: date-time
                        description: 创建时间
                        examples:
                          - ''
                      errorCode:
                        type: integer
                        format: int32
                        description: |-
                          错误码

                          - **200**: 成功 - 请求已成功处理
                          - **500**: 内部错误 - 请稍后再试。
                        enum:
                          - 200
                          - 500
                        examples:
                          - 0
                      errorMessage:
                        type: string
                        description: 错误信息
                        examples:
                          - ''
                    x-apidog-orders:
                      - taskId
                      - musicId
                      - callbackUrl
                      - musicIndex
                      - completeTime
                      - response
                      - successFlag
                      - createTime
                      - errorCode
                      - errorMessage
                    x-apidog-ignore-properties: []
                x-apidog-orders:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  taskId: 988e****c8d3
                  musicId: e231****-****-****-****-****8cadc7dc
                  callbackUrl: https://api.example.com/callback
                  musicIndex: 0
                  completeTime: '2025-01-01 00:10:00'
                  response:
                    videoUrl: https://example.com/s/04e6****e727.mp4
                  successFlag: SUCCESS
                  createTime: '2025-01-01 00:00:00'
                  errorCode: null
                  errorMessage: null
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
      x-apidog-folder: docs/zh-CN/Market/Suno API/Music Video Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506738-run
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
