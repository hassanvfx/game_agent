# Generate sounds

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
      summary: Generate sounds
      deprecated: false
      description: >-
        Used for creating a sound generation task (Sounds Task). It supports
        settings for looping, tempo (BPM), pitch (Key), as well as lyrics
        subtitle capture, etc. 


        ## 🚀 User Guide 

        - By using this interface, you can generate corresponding audio content
        based on the input `prompt`.

        - It supports setting up loop playback effect, which is suitable for
        background music, ambient sounds, and other scenarios.

        - It allows specifying BPM (beats per minute) and pitch (Key) to
        facilitate control over the style of the generated result.

        - Optional feature to enable lyric subtitle capture for easier display
        or processing of lyric content later.

        - Supports asynchronous reception of task completion notifications
        through callback address. 


        ## 📌 Usage Scenarios

        - 🎧 Background music creation

        - 🎮 Game sound effects or looped ambient sounds generation

        - 🌐 Integration of audio content platforms and creative tools


        <Card
          title="Poll Query Results"
          icon="lucide-radar"
          href="/suno-api/get-music-details"
        >
         Use the get lyrics details endpoint to regularly query task status. We recommend querying every 30 seconds.
        </Card>
      operationId: generate-sounds
      tags:
        - docs/en/Market/Suno API/Sounds Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                prompt:
                  description: 'Sound task type limit: 500 characters'
                  type: string
                  title: prompt
                model:
                  type: string
                  title: ''
                  description: Model Name
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
                  description: Is it a cycle?
                  default: false
                soundTempo:
                  type: integer
                  title: BPM:Beats per minute
                  description: Do not broadcast.
                  default: null
                  minimum: 1
                  maximum: 300
                soundKey:
                  type: string
                  title: ''
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
                  title: Grab the lyrics subtitles
                  description: >-
                    Whether to capture the lyrics subtitles 


                    Will the interface be called after completion to obtain the
                    lyrics subtitles?
                  default: false
                callBackUrl:
                  type: string
                  title: Callback address
                  description: Callback user
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
              x-apidog-ignore-properties: []
            example:
              prompt: sint
              model: V5
              soundLoop: true
              soundTempo: 166
              soundKey: D#m
              grabLyrics: true
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApiResponse'
              example:
                code: 422
                msg: success
                data:
                  taskId: task38695****935u9043u
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
      x-apidog-folder: docs/en/Market/Suno API/Sounds Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-31423055-run
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          description: >-
            Response status code


            - **200**: Success - Request has been processed successfully

            - **401**: Unauthorized - Authentication credentials are missing or
            invalid

            - **402**: Insufficient Credits - Account does not have enough
            credits to perform the operation

            - **404**: Not Found - The requested resource or endpoint does not
            exist

            - **422**: Validation Error - The request parameters failed
            validation checks

            - **429**: Rate Limited - Request limit has been exceeded for this
            resource

            - **433**: Request Limit - Sub-key Usage Exceeds Limit

            - **455**: Service Unavailable - System is currently undergoing
            maintenance

            - **500**: Server Error - An unexpected error occurred while
            processing the request

            - **501**: Generation Failed - Content generation task failed

            - **505**: Feature Disabled - The requested feature is currently
            disabled
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
          description: Response message, error description when failed
          examples:
            - success
        data:
          type: object
          properties:
            taskId:
              type: string
              description: >-
                Task ID, can be used with Get Task Details endpoint to query
                task status
          x-apidog-orders:
            - taskId
          required:
            - taskId
          x-apidog-ignore-properties: []
      x-apidog-orders:
        - code
        - msg
        - data
      title: response not with recordId
      required:
        - data
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
