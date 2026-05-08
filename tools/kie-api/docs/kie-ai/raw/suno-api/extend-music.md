# Extend Music

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/extend:
    post:
      summary: Extend Music
      deprecated: false
      description: >-
        Extend or modify existing music by creating a continuation based on a
        source audio track.


        ### Usage Guide

        - This endpoint allows you to extend existing music tracks

        - You can choose to use original parameters or set new custom parameters

        - Extended music will maintain style consistency with the source track


        ### Parameter Details

        - With Custom Parameters (`defaultParamFlag: true`):
          - `prompt`, `style`, `title` and `continueAt` are required
          - Character limits vary by model:
            - **V4**: `prompt` 3000 characters, `style` 200 characters, `title` 80 characters
            - **V4_5 & V4_5PLUS**: `prompt` 5000 characters, `style` 1000 characters, `title` 100 characters
            - **V4_5ALL**: `prompt` 5000 characters, `style` 1000 characters, `title` 80 characters
            - **V5_5 & V5**: `prompt` 5000 characters, `style` 1000 characters, `title` 100 characters

        - With Original Parameters (`defaultParamFlag: false`):
          - Only `audioId` is required
          - Other parameters will be inherited from the source audio

        ### Developer Notes

        - Generated files are retained for 14 days

        - Model version must match the source audio's model version

        - Callback process follows the same pattern as the music generation
        endpoint
      operationId: extend-music
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - defaultParamFlag
                - audioId
                - prompt
                - model
                - callBackUrl
              properties:
                defaultParamFlag:
                  type: boolean
                  description: >-
                    Controls parameter source for extension.  

                    - If `true`: Use custom parameters specified in this
                    request. Requires `continueAt`, `prompt`, `style`, and
                    `title`.  

                    - If `false`: Use original audio parameters. Only `audioId`
                    is required, other parameters are inherited.
                  examples:
                    - true
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the audio track to extend. Required for
                    all extension requests.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                prompt:
                  type: string
                  description: >-
                    Description of the desired audio extension content.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Character limits by model:  
                      - **V4**: Maximum 3000 characters  
                      - **V4_5 & V4_5PLUS**: Maximum 5000 characters  
                      - **V4_5ALL**: Maximum 5000 characters  
                      - **V5_5 & V5**: Maximum 5000 characters  
                    - Describes how the music should continue or change in the
                    extension.
                  examples:
                    - >-
                      Extend the music with more relaxing notes and a gentle
                      bridge section
                style:
                  type: string
                  description: >-
                    Music style specification for the extended audio.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Character limits by model:  
                      - **V4**: Maximum 200 characters  
                      - **V4_5 & V4_5PLUS**: Maximum 1000 characters  
                      - **V4_5ALL**: Maximum 1000 characters  
                      - **V5_5 & V5**: Maximum 1000 characters  
                    - Should typically align with the original audio's style for
                    best results.
                  examples:
                    - Classical
                title:
                  type: string
                  description: |-
                    Title for the extended music track.  
                    - Required when `defaultParamFlag` is `true`.  
                    - Character limits by model:  
                      - **V4**: Maximum 80 characters  
                      - **V4_5 & V4_5PLUS**: Maximum 100 characters  
                      - **V4_5ALL**: Maximum 80 characters  
                      - **V5_5 & V5**: Maximum 100 characters  
                    - Will be displayed in player interfaces and filenames.
                  examples:
                    - Peaceful Piano Extended
                continueAt:
                  type: number
                  description: >-
                    The time point (in seconds) from which to start extending
                    the music.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Value range: greater than 0 and less than the total
                    duration of the generated audio.  

                    - Specifies the position in the original track where the
                    extension should begin.
                  examples:
                    - 60
                model:
                  type: string
                  description: |-
                    The AI model version to use for generation.  
                    - Required for all requests.  
                    - Available options:  
                      - **`V5_5`**：Custom Models Tailored to Your Unique Taste.  
                      - **`V5`**: Superior musical expression, faster generation.  
                      - **`V4_5PLUS`**: V4.5+ delivers richer sound, new ways to create, max 8 min.  
                      - **`V4_5`**: V4.5 enables smarter prompts, faster generations, max 8 min.  
                      - **`V4_5ALL`**: V4.5ALL enables smarter prompts, faster generations, max 8 min.  
                      - **`V4`**: V4 improves vocal quality, max 4 min.
                  enum:
                    - V4
                    - V4_5
                    - V4_5PLUS
                    - V4_5ALL
                    - V5
                    - V5_5
                  examples:
                    - V4
                  x-apidog-enum:
                    - value: V4
                      name: ''
                      description: ''
                    - value: V4_5
                      name: ''
                      description: ''
                    - value: V4_5PLUS
                      name: ''
                      description: ''
                    - value: V4_5ALL
                      name: ''
                      description: ''
                    - value: V5
                      name: ''
                      description: ''
                    - value: V5_5
                      name: ''
                      description: ''
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive music extension task completion updates.
                    Required for all music extension requests.


                    - System will POST task status and results to this URL when
                    extension completes

                    - Callback process has three stages: `text` (text
                    generation), `first` (first track complete), `complete` (all
                    tracks complete)

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing extended track results and audio
                    URLs

                    - For detailed callback format and implementation guide, see
                    [Music Extension
                    Callbacks](https://docs.kie.ai/suno-api/extend-music-callbacks)

                    - Alternatively, use the Get Music Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
                negativeTags:
                  type: string
                  description: >-
                    Music styles or traits to exclude from the extended audio.
                    Optional. Use to avoid specific undesired characteristics.
                  examples:
                    - Heavy Metal, Upbeat Drums
                vocalGender:
                  type: string
                  description: >-
                    Vocal gender preference for the singing voice. Optional. Use
                    'm' for male and 'f' for female. Based on practice, this
                    parameter can only increase the probability but cannot
                    guarantee adherence to male/female voice instructions.
                  enum:
                    - m
                    - f
                  examples:
                    - m
                styleWeight:
                  type: number
                  description: >-
                    Strength of adherence to the specified style. Optional.
                    Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.65
                weirdnessConstraint:
                  type: number
                  description: >-
                    Controls experimental/creative deviation. Optional. Range
                    0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.65
                audioWeight:
                  type: number
                  description: >-
                    Balance weight for audio features vs. other factors.
                    Optional. Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.65
                personaId:
                  type: string
                  description: >-
                    Only available when Custom Mode (`customMode: true`) is
                    enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [](generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  examples:
                    - persona_123
              x-apidog-orders:
                - defaultParamFlag
                - audioId
                - prompt
                - style
                - title
                - continueAt
                - model
                - callBackUrl
                - negativeTags
                - vocalGender
                - styleWeight
                - weirdnessConstraint
                - audioWeight
                - personaId
                - 01KH5V3MA50W3NF9XV737X3882
              x-apidog-refs:
                01KH5V3MA50W3NF9XV737X3882:
                  type: object
                  properties: {}
              x-apidog-ignore-properties: []
            example:
              defaultParamFlag: true
              audioId: e231****-****-****-****-****8cadc7dc
              prompt: >-
                Extend the music with more relaxing notes and a gentle bridge
                section
              model: V4
              callBackUrl: https://api.example.com/callback
              style: Classical
              title: Peaceful Piano Extended
              continueAt: 60
              negativeTags: Heavy Metal, Upbeat Drums
              vocalGender: m
              styleWeight: 0.65
              weirdnessConstraint: 0.65
              audioWeight: 0.65
              personaId: persona_123
              personaModel: style_persona
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
                          - 401
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 451
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request has been processed
                          successfully

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist

                          - **409**: Conflict - WAV record already exists

                          - **422**: Validation Error - The request parameters
                          failed validation checks

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource

                          - **451**: Unauthorized - Failed to fetch the image.
                          Kindly verify any access limits set by you or your
                          service provider.

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request
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
                            description: >-
                              Task ID for tracking task status. Use this ID with
                              the "Get Music Details" endpoint to query
                              extension task details and results.
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
        audioExtend:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when audio generation is
                complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "All generated successfully.",
                  "data": {
                    "callbackType": "complete",
                    "task_id": "2fac****9f72",
                    "data": [
                      {
                        "id": "e231****-****-****-****-****8cadc7dc",
                        "audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
                      },
                      {
                        "id": "bd15****1873",
                        "audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 228.28
                      }
                    ]
                  }
                }

                ```
              requestBody:
                content:
                  application/json:
                    schema:
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
                              description: >-
                                Callback type: text (text generation complete),
                                first (first track complete), complete (all
                                tracks complete)
                              enum:
                                - text
                                - first
                                - complete
                            task_id:
                              type: string
                              description: Task ID
                            data:
                              type: array
                              items:
                                type: object
                                properties:
                                  id:
                                    type: string
                                    description: Audio unique identifier (audioId)
                                  audio_url:
                                    type: string
                                    description: Audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  prompt:
                                    type: string
                                    description: Generation prompt/lyrics
                                  model_name:
                                    type: string
                                    description: Model name used
                                  title:
                                    type: string
                                    description: Music title
                                  tags:
                                    type: string
                                    description: Music tags
                                  createTime:
                                    type: string
                                    description: Creation time
                                    format: date-time
                                  duration:
                                    type: number
                                    description: Audio duration (seconds)
              responses:
                '200':
                  description: Callback received successfully
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
                                  - 408
                                  - 413
                                  - 500
                                  - 501
                                  - 531
                                description: >-
                                  Response status code


                                  - **200**: Success - Request has been
                                  processed successfully

                                  - **400**: Validation Error - Lyrics contained
                                  copyrighted material.

                                  - **408**: Rate Limited - Timeout.

                                  - **413**: Conflict - Uploaded audio matches
                                  existing work of art.

                                  - **500**: Server Error - An unexpected error
                                  occurred while processing the request

                                  - **501**: Audio generation failed.

                                  - **531**: Server Error - Sorry, the
                                  generation failed due to an issue. Your
                                  credits have been refunded. Please try again.
                              msg:
                                type: string
                                description: Error message when code != 200
                                example: success
                      example:
                        code: 200
                        msg: success
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506284-run
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
