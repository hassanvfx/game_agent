# 生成声音

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/sounds:
    post:
      summary: 生成声音
      deprecated: false
      description: |-
        用于创建声音生成任务（Sounds Task）。支持设置循环、节拍（BPM）、音调（Key）以及歌词字幕抓取等功能。

        ## 🚀 使用指南

        - 使用该接口可根据输入的 `prompt` 生成对应的声音内容  
        - 支持设置循环播放效果，适合背景音乐、环境音等场景  
        - 支持指定 BPM（每分钟节拍数）和音调（Key），便于控制生成结果风格  
        - 可选开启歌词字幕抓取，便于后续展示或处理歌词内容  
        - 支持通过回调地址异步接收任务完成通知 

        ## 📌 使用场景
        - 🎧 背景音乐创作
        - 🎮 游戏音效或循环环境音生成
        - 🌐 音频内容平台与创作工具集成

        <Card
          title="轮询查询结果"
          icon="lucide-radar"
          href="/cn/suno-api/get-music-details"
        >
         使用获取音乐详情接口定期查询任务状态，建议每30秒查询一次。
        </Card>
      operationId: generate-sounds
      tags:
        - docs/zh-CN/Market/Suno API/Sounds Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                prompt:
                  description: sounds任务类型限制500字符
                  type: string
                  title: prompt
                model:
                  type: string
                  title: 模型
                  description: 模型名称
                  enum:
                    - V5
                    - V5_5
                  x-apidog-enum:
                    - value: V5
                      name: ''
                      description: ''
                    - value: V5_5
                      name: ''
                      description: ''
                soundLoop:
                  type: boolean
                  title: ''
                  description: 是否循环
                  default: false
                soundTempo:
                  type: integer
                  title: BPM:每分钟节拍数
                  description: 不传就是Auto
                  default: null
                  minimum: 1
                  maximum: 300
                soundKey:
                  type: string
                  title: Key:调性
                  default: Any
                  enum:
                    - Cm
                    - C#m
                    - Dm
                    - D#m
                    - Em
                    - Fm
                    - F#m
                    - Gm
                    - G#m
                    - Am
                    - A#m
                    - Bm
                    - C
                    - C#
                    - D
                    - D#
                    - E
                    - F
                    - F#
                    - G
                    - G#
                    - A
                    - A#
                    - B
                  x-apidog-enum:
                    - value: Cm
                      name: ''
                      description: ''
                    - value: C#m
                      name: ''
                      description: ''
                    - value: Dm
                      name: ''
                      description: ''
                    - value: D#m
                      name: ''
                      description: ''
                    - value: Em
                      name: ''
                      description: ''
                    - value: Fm
                      name: ''
                      description: ''
                    - value: F#m
                      name: ''
                      description: ''
                    - value: Gm
                      name: ''
                      description: ''
                    - value: G#m
                      name: ''
                      description: ''
                    - value: Am
                      name: ''
                      description: ''
                    - value: A#m
                      name: ''
                      description: ''
                    - value: Bm
                      name: ''
                      description: ''
                    - value: C
                      name: ''
                      description: ''
                    - value: C#
                      name: ''
                      description: ''
                    - value: D
                      name: ''
                      description: ''
                    - value: D#
                      name: ''
                      description: ''
                    - value: E
                      name: ''
                      description: ''
                    - value: F
                      name: ''
                      description: ''
                    - value: F#
                      name: ''
                      description: ''
                    - value: G
                      name: ''
                      description: ''
                    - value: G#
                      name: ''
                      description: ''
                    - value: A
                      name: ''
                      description: ''
                    - value: A#
                      name: ''
                      description: ''
                    - value: B
                      name: ''
                      description: ''
                  examples:
                    - Any
                grabLyrics:
                  type: boolean
                  title: 抓取歌词字幕
                  description: |-
                    是否抓取歌词字幕

                    完成后是否调用接口获取歌词字幕
                callBackUrl:
                  type: string
                  title: 回调地址
                  description: 回调用户
              required:
                - prompt
                - model
              x-apidog-orders:
                - prompt
                - model
                - soundLoop
                - soundTempo
                - soundKey
                - grabLyrics
                - callBackUrl
            example:
              prompt: sint
              model: V5
              soundLoop: true
              soundTempo: 166
              soundKey: D#m
              grabLyrics: true
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
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 451
                          - 455
                          - 500
                        description: |-
                          响应状态码

                          - **200**: 成功 - 请求已成功处理  
                          - **401**: 未授权 - 认证凭据缺失或无效  
                          - **402**: 积分不足 - 账户没有足够的积分来执行此操作  
                          - **404**: 未找到 - 请求的资源或端点不存在  
                          - **409**: 冲突 - WAV记录已存在  
                          - **422**: 验证错误 - 请求参数验证失败  
                          - **429**: 速率限制 - 此资源的请求限制已超出  
                          - **451**: 未授权 - 无法获取图像。请验证您或您的服务提供商设置的任何访问限制  
                          - **455**: 服务不可用 - 系统正在进行维护  
                          - **500**: 服务器错误 - 处理请求时发生意外错误
                      msg:
                        type: string
                        description: 当 code != 200 时的错误消息
                        examples:
                          - success
                    x-apidog-orders:
                      - code
                      - msg
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: 用于跟踪任务状态的任务ID。使用此ID与"获取音乐详情"接口查询任务详情和结果。
                            examples:
                              - 5c79****be8e
                        x-apidog-orders:
                          - taskId
                    x-apidog-orders:
                      - data
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
      x-apidog-folder: docs/zh-CN/Market/Suno API/Sounds Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-31420932-run
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
