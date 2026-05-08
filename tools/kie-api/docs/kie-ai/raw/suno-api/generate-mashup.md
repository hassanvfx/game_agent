# Generate Mashup Music

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/mashup:
    post:
      summary: Generate Mashup Music
      deprecated: false
      description: >-
        > Create remix music using AI models by combining multiple audio tracks.


        ## Usage Guide


        - This interface creates remix music from up to 2 uploaded audio files.

        - It combines elements from multiple tracks into a coherent new piece.

        - You can control the level of detail using custom mode and instrumental
        settings.


        ## Parameter Details


        - `uploadUrlList` is required and must contain exactly 2 audio file
        URLs.


        ### In Custom Mode (`customMode: true`)


        Character limits for `prompt` across different models:


        | Model | `prompt` Limit | `style` Limit |

        |:---|:---|:---|

        | **V4** | 3000 characters | 200 characters |

        | **V4_5** and **V4_5PLUS** | 5000 characters | 1000 characters |

        | **V4_5ALL** | 5000 characters | 1000 characters |

        | **V5** and **V5_5** | 5000 characters | 1000 characters |


        - `title` length limit: 80 characters (all models).


        ### In Non-Custom Mode (`customMode: false`)


        - `prompt` length limit: 500 characters.

        - `instrumental`: Whether to generate instrumental music.

        - Other parameters should be left empty.


        ## Developer Notes


        :::tip


        New users are advised to start with `customMode: false`, which is
        simpler.


        :::


        - Generated files will be retained for 14 days.

        - The callback process has three stages: `text` (text generation),
        `first` (first track complete), `complete` (all complete).

        - Uploaded audio files must have publicly accessible URLs.

        - `uploadUrlList` must contain exactly 2 audio file URLs to initiate
        remix generation.


        ## Optional Parameters


        | Parameter | Type | Description |

        |:---|:---|:---|

        | `vocalGender` | string | Vocal gender preference. `m` for male, `f`
        for female. **Note**: This parameter only takes effect when `customMode`
        is `true`. In practice, this parameter only increases the probability
        but does not guarantee adherence to the specified vocal gender. |

        | `styleWeight` | number | Strength of adherence to style. **Note**:
        This parameter only takes effect when `customMode` is `true`. Range is
        0–1, with two decimal places. Example: `0.61`. |

        | `weirdnessConstraint` | number | Creativity/discreteness level.
        **Note**: This parameter only takes effect when `customMode` is `true`.
        Range is 0–1, with two decimal places. Example: `0.72`. |

        | `audioWeight` | number | Weight of audio elements. **Note**: This
        parameter only takes effect when `customMode` is `true`. Range is 0–1,
        with two decimal places. Example: `0.65`. |
      operationId: generate-mashup
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - uploadUrlList
                - style
                - title
                - customMode
                - model
                - callBackUrl
              properties:
                uploadUrlList:
                  type: array
                  description: >-
                    Array of audio file URLs to mashup. Must contain exactly 2
                    URLs. Each URL must be publicly accessible.
                  items:
                    type: string
                    format: uri
                  minItems: 2
                  maxItems: 2
                  examples:
                    - - https://example.com/audio1.mp3
                      - https://example.com/audio2.mp3
                prompt:
                  type: string
                  description: >-
                    A description of the desired audio content.  

                    - In Custom Mode (`customMode: true`): Required if
                    `instrumental` is `false`. The prompt will be strictly used
                    as the lyrics and sung in the generated track. Character
                    limits by model:  
                      - **V4**: Maximum 3000 characters  
                      - **V4_5 & V4_5PLUS**: Maximum 5000 characters  
                      - **V4_5ALL**: Maximum 5000 characters  
                      - **V5 & V5_5**: Maximum 5000 characters  
                      Example: "A calm and relaxing piano track with soft melodies"  
                    - In Non-custom Mode (`customMode: false`): Always required.
                    The prompt serves as the core idea, and lyrics will be
                    automatically generated based on it (not strictly matching
                    the input). Maximum 500 characters.  
                      Example: "A short relaxing piano tune"
                  examples:
                    - A calm and relaxing piano track with soft melodies
                style:
                  type: string
                  description: >-
                    Music style specification for the generated audio.  

                    - Only available and required in Custom Mode (`customMode:
                    true`). Defines the genre, mood, or artistic direction.  

                    - Character limits by model:  
                      - **V4**: Maximum 200 characters  
                      - **V4_5 & V4_5PLUS**: Maximum 1000 characters  
                      - **V4_5ALL**: Maximum 1000 characters  
                      - **V5 & V5_5**: Maximum 1000 characters  
                    - Common examples: Jazz, Classical, Electronic, Pop, Rock,
                    Hip-hop, etc.
                  examples:
                    - Jazz
                title:
                  type: string
                  description: >-
                    Title for the generated music track.  

                    - Only available and required in Custom Mode (`customMode:
                    true`).  

                    - Max length: 80 characters.  

                    - Will be displayed in player interfaces and filenames.
                  examples:
                    - Relaxing Piano
                customMode:
                  type: boolean
                  description: >-
                    Determines if advanced parameter customization is enabled.  

                    - If `true`: Allows detailed control with specific
                    requirements for `style` and `title` fields.  

                    - If `false`: Simplified mode where only `prompt` is
                    required and other parameters are ignored.
                  examples:
                    - true
                instrumental:
                  type: boolean
                  description: >-
                    Determines if the audio should be instrumental (no
                    lyrics).  

                    - In Custom Mode (`customMode: true`):  
                      - If `true`: Only `style` and `title` are required.  
                      - If `false`: `style`, `title`, and `prompt` are required (with prompt used as the exact lyrics).  
                    - In Non-custom Mode (`customMode: false`): No impact on
                    required fields (prompt only).
                  examples:
                    - true
                model:
                  type: string
                  description: |-
                    The AI model version to use for generation.  
                    - Required for all requests.  
                    - Available options:  
                      - **`V5_5`**: Custom Models Tailored to Your Unique Taste.
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
                    The URL to receive music generation task completion updates.
                    Required for all music generation requests.


                    - System will POST task status and results to this URL when
                    generation completes

                    - Callback process has three stages: `text` (text
                    generation), `first` (first track complete), `complete` (all
                    tracks complete)

                    - Note: Some cases may skip `text` and `first` stages and
                    return `complete` directly

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing task results and audio URLs

                    - For detailed callback format and implementation guide, see
                    [Music Generation
                    Callbacks](https://docs.kie.ai/suno-api/generate-music-callbacks)

                    - Alternatively, use the Get Music Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://example.com/callback
                vocalGender:
                  type: string
                  description: >-
                    Vocal gender preference for the singing voice.  

                    - Only available in Custom Mode (`customMode: true`).
                    Optional. Use 'm' for male and 'f' for female. Based on
                    practice, this parameter can only increase the probability
                    but cannot guarantee adherence to male/female voice
                    instructions.
                  enum:
                    - m
                    - f
                  examples:
                    - m
                styleWeight:
                  type: number
                  description: >-
                    Strength of adherence to the specified style.  

                    - Only available in Custom Mode (`customMode: true`).
                    Optional. Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.61
                weirdnessConstraint:
                  type: number
                  description: >-
                    Controls experimental/creative deviation.  

                    - Only available in Custom Mode (`customMode: true`).
                    Optional. Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.72
                audioWeight:
                  type: number
                  description: >-
                    Balance weight for audio features vs. other factors.  

                    - Only available in Custom Mode (`customMode: true`).
                    Optional. Range 0–1, up to 2 decimal places.
                  minimum: 0
                  maximum: 1
                  multipleOf: 0.01
                  examples:
                    - 0.65
              x-apidog-orders:
                - uploadUrlList
                - prompt
                - style
                - title
                - customMode
                - instrumental
                - model
                - callBackUrl
                - vocalGender
                - styleWeight
                - weirdnessConstraint
                - audioWeight
              x-apidog-ignore-properties: []
            example:
              uploadUrlList:
                - https://example.com/audio1.mp3
                - https://example.com/audio2.mp3
              customMode: true
              model: V4
              callBackUrl: https://example.com/callback
              prompt: A calm and relaxing piano track with soft melodies
              style: Jazz
              title: Relaxing Piano
              instrumental: true
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
                          Response Status Codes


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
                          service provider  

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
                              the "Get Music Details" endpoint to query task
                              details and results.
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
          description: 请求失败
          content:
            application/json:
              schema:
                type: object
                properties: {}
                x-apidog-orders: []
                x-apidog-ignore-properties: []
          headers: {}
          x-apidog-name: Error
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506728-run
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
