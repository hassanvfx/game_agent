# Replace Music Section

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/replace-section:
    post:
      summary: Replace Music Section
      deprecated: false
      description: >-
        > Replace a specific time segment within existing music.


        This interface can replace specific time segments in already generated
        music. It requires providing the original music's task ID and the time
        range to be replaced. The replaced audio will naturally blend with the
        original music.


        ## Parameter Details


        ### Required Parameters


        *   `taskId`: Original music's parent task ID

        *   `audioId`: Audio ID to replace

        *   `prompt`: Prompt describing the replacement segment content

        *   `tags`: Music style tags

        *   `title`: Music title

        *   `infillStartS`: Start time point for replacement (seconds, 2 decimal
        places)

        *   `infillEndS`: End time point for replacement (seconds, 2 decimal
        places)


        ### Optional Parameters


        *   `negativeTags`: Music styles to exclude

        *   `fullLyrics`: Complete lyrics after modification, combining both
        modified and unmodified lyrics

        *   `callBackUrl`: Callback address after task completion


        ## Time Range Instructions


        *   `infillStartS` must be less than `infillEndS`.

        *   Time values are precise to 2 decimal places, e.g., `10.50` seconds.

        *   The replacement time range must be between **6 and 60 seconds**.

        *   Replacement duration should not exceed **50%** of the original
        music's total duration.


        ## Developer Notes


        *   Replacement segments will be regenerated based on the provided
        `prompt` and `tags`.

        *   Generated replacement segments will automatically blend with the
        original music's preceding and following parts.

        *   Generated files will be retained for **14 days**.

        *   Query task status using the same interface as generating music: [Get
        Music Details](/suno-api/get-music-details).
      operationId: replace-section
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - prompt
                - tags
                - title
                - infillStartS
                - infillEndS
                - fullLyrics
              properties:
                taskId:
                  type: string
                  description: >-
                    Original task ID (parent task), used to identify the source
                    music for section replacement
                  examples:
                    - 2fac****9f72
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the audio track to replace. This ID is
                    returned in the callback data after music generation
                    completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                prompt:
                  type: string
                  description: Replaced lyrics
                  examples:
                    - A calm and relaxing piano track.
                tags:
                  type: string
                  description: Music style tags, such as jazz, electronic, etc.
                  examples:
                    - Jazz
                title:
                  type: string
                  description: Music title
                  examples:
                    - Relaxing Piano
                negativeTags:
                  type: string
                  description: >-
                    Excluded music styles, used to avoid specific style elements
                    in the replacement segment
                  examples:
                    - Rock
                infillStartS:
                  type: number
                  description: >-
                    Start time point for replacement (seconds), 2 decimal
                    places. Must be less than infillEndS. The time interval
                    (infillEndS - infillStartS) must be between 6 and 60
                    seconds.
                  minimum: 0
                  examples:
                    - 10.5
                infillEndS:
                  type: number
                  description: >-
                    End time point for replacement (seconds), 2 decimal places.
                    Must be greater than infillStartS. The time interval
                    (infillEndS - infillStartS) must be between 6 and 60
                    seconds.
                  minimum: 0
                  examples:
                    - 20.75
                fullLyrics:
                  type: string
                  description: >-
                    Complete lyrics after modification, combining both modified
                    and unmodified lyrics. This parameter contains the full
                    lyrics text that will be used for the entire song after the
                    section replacement.
                  examples:
                    - |-
                      [Verse 1]
                      Original lyrics here
                      [Chorus]
                      Modified lyrics for this section
                      [Verse 2]
                      More original lyrics
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    Callback URL for task completion. The system will send a
                    POST request to this URL when replacement is complete,
                    containing task status and results.


                    - Your callback endpoint should be able to accept POST
                    requests containing JSON payloads with replacement results

                    - For detailed callback format and implementation guide, see
                    [Replace Music Section
                    Callbacks](https://docs.kie.ai/suno-api/replace-section-callbacks)

                    - Alternatively, you can use the get music details interface
                    to poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://example.com/callback
              x-apidog-orders:
                - taskId
                - audioId
                - prompt
                - tags
                - title
                - negativeTags
                - infillStartS
                - infillEndS
                - fullLyrics
                - callBackUrl
              x-apidog-ignore-properties: []
            example:
              taskId: 2fac****9f72
              audioId: e231****-****-****-****-****8cadc7dc
              prompt: A calm and relaxing piano track.
              tags: Jazz
              title: Relaxing Piano
              negativeTags: Rock
              infillStartS: 10.5
              infillEndS: 20.75
              fullLyrics: |-
                [Verse 1]
                Original lyrics here
                [Chorus]
                Modified lyrics for this section
                [Verse 2]
                More original lyrics
              callBackUrl: https://example.com/callback
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


                          - **200**: Success - Request processed successfully

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account does not
                          have enough credits to perform this operation

                          - **404**: Not found - Requested resource or endpoint
                          does not exist

                          - **409**: Conflict - WAV record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limit exceeded - Exceeded request
                          limit for this resource

                          - **451**: Unauthorized - Failed to retrieve image.
                          Please verify any access restrictions set by you or
                          your service provider.

                          - **455**: Service unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request
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
                              Task ID for tracking task status. You can use this
                              ID to query task details and results through the
                              "Get Music Details" interface.
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
                When audio generation is complete, the system will call this
                callback to notify the result.


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
                        "prompt": "A calm and relaxing piano track.",
                        "model_name": "chirp-v3-5",
                        "title": "Relaxing Piano",
                        "tags": "Jazz",
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
                          description: Return message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation complete),
                                first (first song complete), complete (all
                                complete)
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


                                  - **200**: Success - Request processed
                                  successfully

                                  - **400**: Validation error - Lyrics contain
                                  copyrighted content.

                                  - **408**: Rate limit exceeded - Timeout.

                                  - **413**: Conflict - Uploaded audio matches
                                  existing artwork.

                                  - **500**: Server error - Unexpected error
                                  occurred while processing request

                                  - **501**: Audio generation failed.

                                  - **531**: Server error - Sorry, generation
                                  failed due to issues. Your credits have been
                                  refunded. Please try again.
                              msg:
                                type: string
                                description: Error message when code != 200
                                example: success
                      example:
                        code: 200
                        msg: success
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506294-run
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
