# Upload And Cover Audio

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/upload-cover:
    post:
      summary: Upload And Cover Audio
      deprecated: false
      description: >-
        > This API creates a cover version of an audio track by transforming it
        into a new style while retaining its core melody. It incorporates Suno's
        upload capability, enabling users to upload an audio file for
        processing. The expected result is a refreshed audio track with a new
        style, keeping the original melody intact.


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


        *   **When `customMode` is `true` (Custom Mode):**
            *   If `instrumental` is `true`: `style`, `title`, and `uploadUrl` are required.
            *   If `instrumental` is `false`: `style`, `prompt`, `title`, and `uploadUrl` are required.
            *   **Character limits vary by model version** (see note above).
            *   `uploadUrl` is used to specify the upload location of the audio file; ensure the uploaded audio does not exceed 8 minutes in length.

        *   **When `customMode` is `false` (Non-custom Mode):**
            *   Only `prompt` and `uploadUrl` are required, regardless of the `instrumental` setting.
            *   `prompt` length limit: 500 characters.
            *   Other parameters should be left empty.

        ## Developer Notes


        1.  **Quick Start for New Users:** Set `customMode` to `false`,
        `instrumental` to `false`, and provide only `prompt` and `uploadUrl`.
        This is the simplest configuration to quickly test the API and
        experience the results.

        2.  Generated files will be deleted after **15 days**.

        3.  Ensure all required parameters are provided based on the
        `customMode` and `instrumental` settings to avoid errors.

        4.  Pay attention to character limits for `prompt`, `style`, and `title`
        to ensure successful processing.

        5.  **Callback Process Stages:** The callback process has three stages:
        `text` (text generation complete), `first` (first track complete), and
        `complete` (all tracks complete).

        6.  **Active Status Check:** You can use the [Get Music Generation
        Details](/suno-api/get-music-details) endpoint to actively check the
        task status instead of waiting for callbacks.

        7.  The `uploadUrl` parameter is used to specify the upload location of
        the audio file; please provide a valid URL.


        ## Optional Parameters


        *   `vocalGender` (`string`): Vocal gender preference. Use `m` for male,
        `f` for female.

        *   `styleWeight` (`number`): Strength of adherence to style. Range 0–1,
        up to 2 decimal places. Example: `0.65`.

        *   `weirdnessConstraint` (`number`): Controls creative deviation. Range
        0–1, up to 2 decimal places. Example: `0.65`.

        *   `audioWeight` (`number`): Balance weight for audio features. Range
        0–1, up to 2 decimal places. Example: `0.65`.

        *   `personaId` (`string`): Persona ID to apply to the generated music.
        Only available when Custom Mode is enabled (i.e., `customMode` is
        `true`). To create one, use [Generate
        Persona](/suno-api/generate-persona).
      operationId: upload-and-cover-audio
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
                - prompt
                - customMode
                - instrumental
                - model
                - callBackUrl
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL for uploading audio files, required regardless of
                    whether customMode and instrumental are true or false.
                    Ensure the uploaded audio does not exceed 8 minutes in
                    length.
                  examples:
                    - https://storage.example.com/upload
                prompt:
                  type: string
                  description: >-
                    A description of the desired audio content.  

                    - In Custom Mode (`customMode: true`):  Required if
                    `instrumental` is `false`. The prompt will be strictly used
                    as the lyrics and sung in the generated track. Character
                    limits by model:  
                      - **V5_5 & V5**: Maximum 5000 characters  
                      - **V4_5PLUS & V4_5**: Maximum 5000 characters  
                      - **V4_5ALL**: Maximum 5000 characters  
                      - **V4**: Maximum 3000 characters  
                      Example: "A calm and relaxing piano track with soft melodies"  
                    - In Non-custom Mode (`customMode: false`): Always required.
                    The prompt serves as the core idea, and lyrics will be
                    automatically generated based on it (not strictly matching
                    the input). Max length: 500 characters.  
                      Example: "A short relaxing piano tune" 
                  examples:
                    - A calm and relaxing piano track with soft melodies
                style:
                  type: string
                  description: >-
                    The music style or genre for the audio.  

                    - Required in Custom Mode (`customMode: true`). Examples:
                    "Jazz", "Classical", "Electronic". Character limits by
                    model:  
                      - **V5_5 & V5**: Maximum 1000 characters  
                      - **V4_5PLUS & V4_5**: Maximum 1000 characters  
                      - **V4_5ALL**: Maximum 1000 characters  
                      - **V4**: Maximum 200 characters  
                      Example: "Classical"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  examples:
                    - Classical
                title:
                  type: string
                  description: >-
                    The title of the generated music track.  

                    - Required in Custom Mode (`customMode: true`). Character
                    limits by model:  
                      - **V5_5 & V5**: Maximum 100 characters  
                      - **V4_5PLUS & V4_5**: Maximum 100 characters  
                      - **V4_5ALL**: Maximum 80 characters  
                      - **V4**: Maximum 80 characters  
                      Example: "Peaceful Piano Meditation"  
                    - In Non-custom Mode (`customMode: false`): Leave empty.
                  examples:
                    - Peaceful Piano Meditation
                customMode:
                  type: boolean
                  description: >-
                    Enables Custom Mode for advanced audio generation
                    settings.  

                    - Set to `true` to use Custom Mode (requires `style` and
                    `title`; `prompt` required if `instrumental` is `false`).
                    The prompt will be strictly used as lyrics if `instrumental`
                    is `false`.  

                    - Set to `false` for Non-custom Mode (only `prompt` is
                    required). Lyrics will be auto-generated based on the
                    prompt.
                  examples:
                    - true
                instrumental:
                  type: boolean
                  description: >-
                    Determines if the audio should be instrumental (no
                    lyrics).  

                    - In Custom Mode (`customMode: true`):  
                      - If `true`: Only `style` and `title` are required.  
                      - If `false`: `style`, `title`, and `prompt` are required (with `prompt` used as the exact lyrics).  
                    - In Non-custom Mode (`customMode: false`): No impact on
                    required fields (`prompt` only). Lyrics are auto-generated
                    if `instrumental` is `false`.
                  examples:
                    - true
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
                  description: >-
                    Music styles or traits to exclude from the generated
                    audio.  

                    - Optional. Use to avoid specific styles.  
                      Example: "Heavy Metal, Upbeat Drums"
                  examples:
                    - Heavy Metal, Upbeat Drums
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive audio covering task completion updates.
                    Required for all audio covering requests.


                    - System will POST task status and results to this URL when
                    audio covering completes

                    - Callback includes generated covered audio files with new
                    style while preserving original melody

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing covered track results and audio URLs

                    - For detailed callback format and implementation guide, see
                    [Audio Covering
                    Callbacks](https://docs.kie.ai/suno-api/upload-and-cover-audio-callbacks)

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
                    'm' for male and 'f' for female. Note: This parameter is
                    only effective when customMode is true. Based on practice,
                    this parameter can only increase the probability but cannot
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


                    To generate a persona ID, use the [Generate
                    Persona](https://docs.kie.ai/suno-api/generate-persona)
                    endpoint to create a personalized music Persona based on
                    generated music.
                  examples:
                    - persona_123
              x-apidog-orders:
                - uploadUrl
                - prompt
                - style
                - title
                - customMode
                - instrumental
                - model
                - negativeTags
                - callBackUrl
                - vocalGender
                - styleWeight
                - weirdnessConstraint
                - audioWeight
                - personaId
                - 01KH5V41Q3E8XKP9P8AJVPBG98
              x-apidog-refs:
                01KH5V41Q3E8XKP9P8AJVPBG98:
                  type: object
                  properties: {}
              x-apidog-ignore-properties: []
            example:
              uploadUrl: https://storage.example.com/upload
              prompt: A calm and relaxing piano track with soft melodies
              customMode: true
              instrumental: true
              model: V4
              callBackUrl: https://api.example.com/callback
              style: Classical
              title: Peaceful Piano Meditation
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
        audioGenerated:
          '{request.body#/callBackUrl}':
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
                      },
                      {
                        "id": "bd15****1873",
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506285-run
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
