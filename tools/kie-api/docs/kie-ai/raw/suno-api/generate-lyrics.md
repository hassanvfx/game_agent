# Generate Lyrics

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/lyrics:
    post:
      summary: Generate Lyrics
      deprecated: false
      description: >-
        Generate creative lyrics content based on a text prompt.


        ### Usage Guide

        - Use this endpoint to create lyrics for music composition

        - Multiple variations of lyrics will be generated for each request

        - Each generated lyric set includes title and structured verse/chorus
        sections


        ### Parameter Details

        - `prompt` should describe the theme, style, or subject of the desired
        lyrics

        - A detailed prompt yields more targeted and relevant lyrics


        ### Developer Notes

        - Generated lyrics are retained for 14 days

        - Callback occurs once with all generated variations when complete

        - Typically returns 2-3 different lyric variations per request

        - Each lyric set is formatted with standard section markers ([Verse],
        [Chorus], etc.)
      operationId: generate-lyrics
      tags:
        - docs/en/Market/Suno API/Lyrics Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - prompt
              properties:
                prompt:
                  type: string
                  description: >-
                    Description of the desired lyrics content. Be specific about
                    theme, mood, style, or story elements you want in the
                    lyrics. More detailed prompts yield better results. The
                    maximum word limit is 200 characters.
                  examples:
                    - >-
                      A nostalgic song about childhood memories and growing up
                      in a small town
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive lyrics generation task completion
                    updates. Required for all lyrics generation requests.


                    - System will POST task status and results to this URL when
                    lyrics generation completes

                    - Callback includes all generated lyrics variations with
                    titles and structured content

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing lyrics data

                    - For detailed callback format and implementation guide, see
                    [Lyrics Generation
                    Callbacks](https://docs.kie.ai/suno-api/generate-lyrics-callbacks)

                    - Alternatively, use the Get Lyrics Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
              x-apidog-orders:
                - prompt
                - callBackUrl
              x-apidog-ignore-properties: []
            example:
              prompt: >-
                A nostalgic song about childhood memories and growing up in a
                small town
              callBackUrl: https://api.example.com/callback
      responses:
        '200':
          description: Request successful
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
                          - 404
                          - 405
                          - 413
                          - 429
                          - 430
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Request successful

                          - **400**: Invalid parameters

                          - **401**: Unauthorized access

                          - **404**: Invalid request method or path

                          - **405**: Rate limit exceeded

                          - **413**: Theme or prompt too long

                          - **429**: Insufficient credits

                          - **430**: Your call frequency is too high. Please try
                          again later.

                          - **455**: System maintenance

                          - **500**: Server error
                      msg:
                        type: string
                        description: Error message when code != 200
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
                            description: Task ID for tracking task status
                            examples:
                              - 5c79****be8e
                        x-apidog-orders:
                          - taskId
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
          headers: {}
          x-apidog-name: ''
        '500':
          description: request failed
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: >-
                      Response status code


                      - **200**: Success - Request has been processed
                      successfully

                      - **401**: Unauthorized - Authentication credentials are
                      missing or invalid

                      - **402**: Insufficient Credits - Account does not have
                      enough credits to perform the operation

                      - **404**: Not Found - The requested resource or endpoint
                      does not exist

                      - **408**: Upstream is currently experiencing service
                      issues. No result has been returned for over 10 minutes.

                      - **422**: Validation Error - The request parameters
                      failed validation checks

                      - **429**: Rate Limited - Request limit has been exceeded
                      for this resource

                      - **455**: Service Unavailable - System is currently
                      undergoing maintenance

                      - **500**: Server Error - An unexpected error occurred
                      while processing the request

                      - **501**: Generation Failed - Content generation task
                      failed

                      - **505**: Feature Disabled - The requested feature is
                      currently disabled
                  msg:
                    type: string
                    description: Response message, error description when failed
                  data:
                    type: object
                    properties: {}
                    x-apidog-orders: []
                    x-apidog-ignore-properties: []
                x-apidog-orders:
                  - code
                  - msg
                  - data
                required:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 500
                msg: >-
                  Server Error - An unexpected error occurred while processing
                  the request
                data: null
          headers: {}
          x-apidog-name: 'Error '
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
        audioLyricsGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when lyrics generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "data": {
                    "callbackType": "complete",
                    "data": [
                      {
                        "error_message": "",
                        "status": "complete",
                        "text": "[Verse]\n月光洒满了窗台\n星星跳舞不分开\n夜风偷偷织梦来\n心里压抑全抛开\n\n[Verse 2]\n灯火映在你的眼\n像流星划过了天\n世界静止就一瞬间\n追逐未来不管多远\n\n[Chorus]\n星夜梦中找未来\n跳脱平凡别徘徊\n所有的梦都会盛开\n别害怕追去期待\n\n[Verse 3]\n脚步踏着影子走\n黑夜舞曲化解愁\n无声的美比喧嚣\n随心漂流是追求\n\n[Bridge]\n别让时钟锁住天\n别让怀疑把梦编\n逆着风也会更鲜艳\n陪你走过所有难关\n\n[Chorus]\n星夜梦中找未来\n跳脱平凡别徘徊\n所有的梦都会盛开\n别害怕追去期待",
                        "title": "星夜狂想"
                      },
                      {
                        "error_message": "",
                        "status": "complete",
                        "text": "[Verse]\n天边的云跳舞在风里\n追逐梦想越过山和溪\n每一步都写下新的故事\n心中燃烧永不熄的信念\n\n[Verse 2]\n城市的灯照亮午夜的街\n人潮散开我依旧不妥协\n破碎的梦拼凑新的世界\n每一次失败都是一种体验\n\n[Chorus]\n你好你好未来的自己\n你会感激今天的努力\n跌倒再站起笑对这天地\n燃烧吧青春像烈火不息\n\n[Verse 3]\n窗外的雨敲打着玻璃\n像是为我撑起一片绿地\n彷徨的路透过心的指引\n找到方向我无所畏惧\n\n[Bridge]\n耳边风吹散记忆的灰\n让过去成为最美的点缀\n未来的路上脚步更坚定\n看清自己的模样多么耀眼\n\n[Chorus]\n你好你好未来的自己\n你会感激今天的努力\n跌倒再站起笑对这天地\n燃烧吧青春像烈火不息",
                        "title": "你好"
                      }
                    ],
                    "task_id": "3b66882fde0a5d398bd269cab6d9542b"
                  },
                  "msg": "All generated successfully."
                }

                ```
              requestBody:
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
                                - 500
                              description: >-
                                Response status code


                                - **200**: Success - Request has been processed
                                successfully

                                - **400**: Please try rephrasing   with more
                                specific details or using a different approach.

                                Song Description contained artist name

                                Song Description flagged for moderation

                                Unable to generate lyrics from song  
                                description

                                - **500**: Internal Error - Please try again
                                later.
                            msg:
                              type: string
                              description: Error message when code != 200
                              example: success
                        - type: object
                          properties:
                            data:
                              type: object
                              properties:
                                taskId:
                                  type: string
                                  description: Task ID for tracking task status
                                  example: 5c79****be8e
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: Callback type, fixed as complete
                              enum:
                                - complete
                              example: complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              description: Generated lyrics list
                              items:
                                type: object
                                properties:
                                  text:
                                    type: string
                                    description: Lyrics content
                                  title:
                                    type: string
                                    description: Lyrics title
                                  status:
                                    type: string
                                    description: Generation status
                                    enum:
                                      - complete
                                      - failed
                                  error_message:
                                    type: string
                                    description: Error message, valid when status is failed
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Suno API/Lyrics Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506296-run
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
