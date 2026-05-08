# Upload And Extend Audio

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/upload-extend:
    post:
      summary: Upload And Extend Audio
      deprecated: false
      description: >-
        > This API extends audio tracks while preserving their original style.
        It includes Suno's upload functionality, allowing users to upload audio
        files for processing. The expected result is a longer track that
        seamlessly continues the input style.


        ## Parameter Usage Guide


        :::note Character Limits

        Character limits vary depending on the model version:


        *   **Model V5_5 and V5**: `style` (max 1000 chars), `title` (max 100
        chars), `prompt` (max 5000 chars)

        *   **Models V4.5PLUS and V4.5**: `style` (max 1000 chars), `title` (max
        100 chars), `prompt` (max 5000 chars)

        *   **Model V4.5ALL**: `style` (max 1000 chars), `title` (max 80 chars),
        `prompt` (max 5000 chars)

        *   **Model V4**: `style` (max 200 chars), `title` (max 80 chars),
        `prompt` (max 3000 chars)

        :::


        *   **When `defaultParamFlag` is `true` (Custom Parameters):**
            *   If `instrumental` is `true`: `style`, `title`, and `uploadUrl` are required.
            *   If `instrumental` is `false`: `style`, `prompt`, `title`, and `uploadUrl` are required.
            *   **Character limits vary by model version** (see note above).
            *   `continueAt`: The time point in seconds from which to start extending (must be greater than 0 and less than the uploaded audio duration).
            *   `uploadUrl`: Specifies the upload location for audio files; ensure uploaded audio does not exceed 8 minutes.

        *   **When `defaultParamFlag` is `false` (Default Parameters):**
            *   Regardless of the `instrumental` setting, only `uploadUrl` and `prompt` are required.
            *   Other parameters will use the original audio's parameters.

        ## Developer Notes


        1.  Generated files will be retained for **14 days**.

        2.  The model version used must be consistent with the source music's
        model version.

        3.  This feature is ideal for creating longer works by extending
        existing music.

        4.  The `uploadUrl` parameter specifies the upload location for audio
        files; provide a valid URL.


        ## Optional Parameters


        *   `vocalGender` (`string`): Vocal gender preference. Use `m` for male,
        `f` for female.

        *   `styleWeight` (`number`): Strength of adherence to the style. Range
        0–1, up to 2 decimal places. Example: `0.65`.

        *   `weirdnessConstraint` (`number`): Controls creative deviation. Range
        0–1, up to 2 decimal places. Example: `0.65`.

        *   `audioWeight` (`number`): Balance weight for audio features. Range
        0–1, up to 2 decimal places. Example: `0.65`.

        *   `personaId` (`string`): Persona ID to apply to the generated music.
        Only available when Custom Mode is enabled (i.e., `defaultParamFlag` is
        `true`). To create one, use [Generate
        Persona](https://docs.kie.ai/suno-api/generate-persona).
      operationId: upload-and-extend-audio
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrl
                - defaultParamFlag
                - instrumental
                - continueAt
                - model
                - callBackUrl
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL for uploading audio files, required regardless of
                    whether defaultParamFlag is true or false. Ensure the
                    uploaded audio does not exceed 8 minutes in length.
                  examples:
                    - https://storage.example.com/upload
                defaultParamFlag:
                  type: boolean
                  description: >-
                    Enable custom mode for advanced audio generation settings.  

                    - Set to `true` to use custom parameter mode (requires
                    `style`, `title`, and `uploadUrl`; if `instrumental` is
                    `false`, `uploadUrl` and `prompt` are required). If
                    `instrumental` is `false`, the prompt will be strictly used
                    as lyrics.  

                    - Set to `false` to use non-custom mode (only `uploadUrl`
                    required). Lyrics will be automatically generated based on
                    the prompt.
                  examples:
                    - true
                instrumental:
                  type: boolean
                  description: >-
                    Determines whether the audio is instrumental (without
                    lyrics).  

                    - In custom parameter mode (`customMode: true`):  
                      - If `true`: only `style`, `title`, and `uploadUrl` are required.  
                      - If `false`: `style`, `title`, `prompt` (`prompt` will be used as exact lyrics), and `uploadUrl` are required.  
                    - In non-custom parameter mode (`defaultParamFlag: false`):
                    does not affect required fields (only `uploadUrl` needed).
                    If `false`, lyrics will be automatically generated.
                  examples:
                    - true
                prompt:
                  type: string
                  description: >-
                    Description of how the music should be extended. Required
                    when defaultParamFlag is true. Character limits by model:  

                    - **V5_5 & V5**: Maximum 5000 characters  

                    - **V4_5PLUS & V4_5**: Maximum 5000 characters  

                    - **V4_5ALL**: Maximum 5000 characters  

                    - **V4**: Maximum 3000 characters
                  examples:
                    - Extend the music with more relaxing notes
                style:
                  type: string
                  description: >-
                    Music style, e.g., Jazz, Classical, Electronic. Character
                    limits by model:  

                    - **V5_5 & V5**: Maximum 1000 characters  

                    - **V4_5PLUS & V4_5**: Maximum 1000 characters  

                    - **V4_5ALL**: Maximum 1000 characters  

                    - **V4**: Maximum 200 characters
                  examples:
                    - Classical
                title:
                  type: string
                  description: |-
                    Music title. Character limits by model:  
                    - **V5_5 & V5**: Maximum 100 characters  
                    - **V4_5PLUS & V4_5**: Maximum 100 characters  
                    - **V4_5ALL**: Maximum 80 characters  
                    - **V4**: Maximum 80 characters
                  examples:
                    - Peaceful Piano Extended
                continueAt:
                  type: number
                  description: >-
                    The time point (in seconds) from which to start extending
                    the music.  

                    - Required when `defaultParamFlag` is `true`.  

                    - Value range: greater than 0 and less than the total
                    duration of the uploaded audio.  

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
                negativeTags:
                  type: string
                  description: Music styles to exclude from generation
                  examples:
                    - Relaxing Piano
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive audio extension task completion updates.
                    Required for all audio extension requests.


                    - System will POST task status and results to this URL when
                    audio extension completes

                    - Callback includes extended audio files that seamlessly
                    continue the uploaded track's style

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing extended track results and audio
                    URLs

                    - For detailed callback format and implementation guide, see
                    [Audio Extension
                    Callbacks](https://docs.kie.ai/suno-api/upload-and-extend-audio-callbacks)

                    - Alternatively, use the Get Music Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
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
                    Only available when Custom Mode (`defaultParamFlag: true`)
                    is enabled. Persona ID to apply to the generated music.
                    Optional. Use this to apply a specific persona style to your
                    music generation. 


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.kie.ai/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  examples:
                    - persona_123
              x-apidog-orders:
                - uploadUrl
                - defaultParamFlag
                - instrumental
                - prompt
                - style
                - title
                - continueAt
                - model
                - negativeTags
                - callBackUrl
                - vocalGender
                - styleWeight
                - weirdnessConstraint
                - audioWeight
                - personaId
                - 01KH5V4EJ53J4835SRBTS01PZG
              x-apidog-refs:
                01KH5V4EJ53J4835SRBTS01PZG:
                  type: object
                  properties: {}
              x-apidog-ignore-properties: []
            example:
              uploadUrl: https://storage.example.com/upload
              defaultParamFlag: true
              instrumental: true
              continueAt: 60
              model: V4
              callBackUrl: https://api.example.com/callback
              prompt: Extend the music with more relaxing notes
              style: Classical
              title: Peaceful Piano Extended
              negativeTags: Relaxing Piano
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
                        "source_audio_url": "https://example.cn/****.mp3",
                        "stream_audio_url": "https://example.cn/****",
                        "source_stream_audio_url": "https://example.cn/****",
                        "image_url": "https://example.cn/****.jpeg",
                        "source_image_url": "https://example.cn/****.jpeg",
                        "prompt": "[Verse] Night city lights shining bright",
                        "model_name": "chirp-v3-5",
                        "title": "Iron Man",
                        "tags": "electrifying, rock",
                        "createTime": "2025-01-01 00:00:00",
                        "duration": 198.44
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
                                  source_audio_url:
                                    type: string
                                    description: Original audio file URL
                                  stream_audio_url:
                                    type: string
                                    description: Streaming audio URL
                                  source_stream_audio_url:
                                    type: string
                                    description: Original streaming audio URL
                                  image_url:
                                    type: string
                                    description: Cover image URL
                                  source_image_url:
                                    type: string
                                    description: Original cover image URL
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506286-run
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
