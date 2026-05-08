# Add Instrumental to Music

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/add-instrumental:
    post:
      summary: Add Instrumental to Music
      deprecated: false
      description: >-
        Generate instrumental accompaniment based on uploaded audio files. This
        interface allows you to upload audio files and add instrumental tracks
        to them.


        ### Usage Guide

        - Use this interface to add instrumental tracks to existing audio

        - Supports generation of various music style accompaniments

        - Allows customization of style, exclusion of specific elements, etc.


        ### Parameter Details

        - `uploadUrl` specifies the audio file URL to be processed

        - `title` specifies the title for the generated music

        - `tags` and `negativeTags` are used to control music style

        - Supports various optional parameters for fine-tuning generation
        effects


        ### Developer Notes

        - Generated files will be retained for 14 days

        - Callback process has three stages: `text` (text generation), `first`
        (first track completed), `complete` (all completed)
      operationId: add-instrumental
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
                - title
                - negativeTags
                - tags
                - callBackUrl
              properties:
                uploadUrl:
                  type: string
                  format: uri
                  description: >-
                    URL of the uploaded audio file. Specifies the source audio
                    file location for adding accompaniment.
                  examples:
                    - https://example.com/music.mp3
                model:
                  type: string
                  description: |-
                    The AI model version to use for generation.   
                    - Available options: 
                      - **`V5_5`**：Custom Models Tailored to Your Unique Taste.  
                      - **`V5`**: Superior musical expression, faster generation.  
                      - **`V4_5PLUS`**: V4.5+ is richer sound, new ways to create.  
                  enum:
                    - V4_5PLUS
                    - V5
                    - V5_5
                  default: V4_5PLUS
                  examples:
                    - V4_5PLUS
                  x-apidog-enum:
                    - value: V4_5PLUS
                      name: ''
                      description: ''
                    - value: V5
                      name: ''
                      description: ''
                    - value: V5_5
                      name: ''
                      description: ''
                title:
                  type: string
                  description: >-
                    Title of the generated music. Will be displayed in the
                    player interface and file name.
                  examples:
                    - Relaxing Piano
                negativeTags:
                  type: string
                  description: >-
                    Music styles or characteristics to exclude from the
                    generated audio. Used to avoid specific unwanted music
                    elements.
                  examples:
                    - heavy metal, fast drums
                tags:
                  type: string
                  description: >-
                    Music styles or tags to include in the generated music.
                    Defines the desired music style and characteristics.
                  examples:
                    - relaxing, piano, soothing
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    URL address for receiving instrumental generation task
                    completion updates. This parameter is required for all
                    instrumental generation requests.


                    - The system will send a POST request to this URL when
                    instrumental generation is completed, including task status
                    and results

                    - Callback process has three stages: `text` (text
                    generation), `first` (first track completed), `complete`
                    (all completed)

                    - Your callback endpoint should be able to accept POST
                    requests containing JSON payloads with music generation
                    results

                    - Alternatively, you can use the get music details interface
                    to poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://example.com/callback
                vocalGender:
                  type: string
                  description: >-
                    Vocal gender preference. Optional. 'm' for male, 'f' for
                    female. Based on practice, this parameter can only increase
                    the probability but cannot guarantee adherence to
                    male/female voice instructions.
                  enum:
                    - m
                    - f
                  examples:
                    - m
                styleWeight:
                  type: number
                  description: >-
                    Adherence strength to specified style. Optional. Range 0–1,
                    up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.61
                weirdnessConstraint:
                  type: number
                  description: >-
                    Controls experimental/creative deviation level. Optional.
                    Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.72
                audioWeight:
                  type: number
                  description: >-
                    Relative weight of audio elements. Optional. Range 0–1, up
                    to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.65
              x-apidog-orders:
                - uploadUrl
                - model
                - title
                - negativeTags
                - tags
                - callBackUrl
                - vocalGender
                - styleWeight
                - weirdnessConstraint
                - audioWeight
              x-apidog-ignore-properties: []
            example:
              uploadUrl: https://example.com/music.mp3
              title: Relaxing Piano
              negativeTags: heavy metal, fast drums
              tags: relaxing, piano, soothing
              callBackUrl: https://example.com/callback
              model: V4_5PLUS
              vocalGender: m
              styleWeight: 0.61
              weirdnessConstraint: 0.72
              audioWeight: 0.65
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

                          - **429**: Rate limit exceeded - Request limit for
                          this resource has been exceeded

                          - **451**: Unauthorized - Failed to retrieve image.
                          Please verify any access restrictions set by you or
                          your service provider.

                          - **455**: Service unavailable - System currently
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
                When instrumental generation is completed, the system will call
                this callback to notify the results.


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
                        "model_name": "chirp-v4-5",
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
                          description: Return message
                          example: All generated successfully
                        data:
                          type: object
                          properties:
                            callbackType:
                              type: string
                              description: >-
                                Callback type: text (text generation completed),
                                first (first track completed), complete (all
                                completed)
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506287-run
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
