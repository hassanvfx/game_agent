# Generate MIDI from Audio

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/midi/generate:
    post:
      summary: Generate MIDI from Audio
      deprecated: false
      description: >-
        > Convert separated audio tracks into MIDI format with detailed note
        information for each instrument.


        ## Usage Guide


        * Convert separated audio tracks into structured MIDI data containing
        pitch, timing, and velocity information

        * Requires a completed vocal separation task ID (from the Vocal Removal
        API)

        * Generates MIDI note data for multiple detected instruments including
        drums, bass, guitar, keyboards, and more

        * Ideal for music transcription, notation, remixing, or educational
        analysis

        * Best results on clean, well-separated audio tracks with clear
        instrument parts


        ## Prerequisites


        :::warning Required

        You must first use the [Vocal & Instrument Stem
        Separation](/suno-api/separate-vocals) API to separate your audio before
        generating MIDI.

        :::


        ## Parameter Reference


        | Name | Type | Description |

        | :--- | :--- | :--- |

        | **`taskId`** | string | **Required.** Task ID from a completed vocal
        separation. |

        | **`callBackUrl`** | string | **Required.** URL to receive MIDI
        generation completion notifications. |

        | **`audioId`** | string | **Optional.** Specifies which separated audio
        track to generate MIDI from. This `audioId` can be obtained from the
        `originData` array in the [Get Vocal Separation
        Details](/suno-api/get-vocal-separation-details) endpoint response. Each
        item in `originData` contains an `id` field that can be used here. If
        not provided, MIDI will be generated from all separated tracks. |


        ## Developer Notes


        * The callback will contain detailed note data for each detected
        instrument.

        * Each note includes: `pitch` (MIDI note number), `start` (seconds),
        `end` (seconds), `velocity` (0-1).

        * Not all instruments may be detected — depends on audio content.

        * **Pricing:** Check current per-call credit costs at
        [**https://kie.ai/pricing**](https://kie.ai/pricing).
      operationId: generate-midi
      tags:
        - docs/en/Market/Suno API/Vocal Removal
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: >-
                    Task ID from a completed vocal separation. This should be
                    the taskId returned from the Vocal & Instrument Stem
                    Separation endpoint.
                  examples:
                    - 5c79****be8e
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive MIDI generation task completion updates.
                    Required for all MIDI generation requests.


                    - System will POST task status and MIDI note data to this
                    URL when generation completes

                    - Callback includes detailed note information for each
                    detected instrument with pitch, timing, and velocity

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing MIDI data

                    - For detailed callback format and implementation guide, see
                    [MIDI Generation
                    Callbacks](https://docs.kie.ai/suno-api/generate-midi-callbacks)

                    - Alternatively, use the Get MIDI Generation Details
                    endpoint to poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://example.callback
                audioId:
                  type: string
                  description: >-
                    Optional. Specifies which separated audio track to generate
                    MIDI from. This audioId can be obtained from the
                    `originData` array in the Get Vocal Separation Details
                    endpoint response. Each item in `originData` contains an
                    `id` field that can be used here. If not provided, MIDI will
                    be generated from all separated tracks.
                  examples:
                    - 8ca376e7-******-08aaf2c6dd27
              x-apidog-orders:
                - taskId
                - callBackUrl
                - audioId
              x-apidog-ignore-properties: []
            example:
              taskId: 5c79****be8e
              callBackUrl: https://example.callback
              audioId: 8ca376e7-******-08aaf2c6dd27
      responses:
        '200':
          description: MIDI generation task created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: Response status code
                    examples:
                      - 200
                  msg:
                    type: string
                    description: Response message
                    examples:
                      - success
                  data:
                    type: object
                    description: Response data containing task information
                    properties:
                      taskId:
                        type: string
                        description: >-
                          Unique identifier for the MIDI generation task. Use
                          this to query task status or receive callback results.
                        examples:
                          - 5c79****be8e
                    x-apidog-orders:
                      - taskId
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
                  taskId: 5c79****be8e
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
      x-apidog-folder: docs/en/Market/Suno API/Vocal Removal
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506302-run
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
