# Get Timestamped Lyrics

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/get-timestamped-lyrics:
    post:
      summary: Get Timestamped Lyrics
      deprecated: false
      description: >-
        Retrieve synchronized lyrics with precise timestamps for music tracks.


        ### Usage Guide

        - Use this endpoint to get lyrics that synchronize with audio playback

        - Implement karaoke-style lyric displays in your music players

        - Create visualizations that match audio timing


        ### Parameter Details

        - Both `taskId` and `audioId` are required to identify the specific
        track

        - The `taskId` comes from either "Generate Music" or "Extend Music"
        endpoints

        - The `audioId` identifies the specific track version when multiple were
        generated


        ### Developer Notes

        - Timestamps are provided in seconds for precise synchronization

        - Waveform data is included for audio visualization implementations

        - For instrumental tracks (created with `instrumental=true`), no lyrics
        data will be returned
      operationId: get-timestamped-lyrics
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
              properties:
                taskId:
                  type: string
                  description: >-
                    Unique identifier of the music generation task. This should
                    be a taskId returned from either the "Generate Music" or
                    "Extend Music" endpoints.
                  examples:
                    - 5c79****be8e
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the specific audio track for which to
                    retrieve lyrics. This ID is returned in the callback data
                    after music generation completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
              x-apidog-orders:
                - taskId
                - audioId
              x-apidog-ignore-properties: []
            example:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
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
                          - 404
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

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist

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
                          alignedWords:
                            type: array
                            description: List of aligned lyrics words
                            items:
                              type: object
                              properties:
                                word:
                                  type: string
                                  description: Lyrics word
                                  examples:
                                    - |-
                                      [Verse]
                                      Waggin'
                                success:
                                  type: boolean
                                  description: Whether lyrics word is successfully aligned
                                  examples:
                                    - true
                                startS:
                                  type: number
                                  description: Word start time (seconds)
                                  examples:
                                    - 1.36
                                endS:
                                  type: number
                                  description: Word end time (seconds)
                                  examples:
                                    - 1.79
                                palign:
                                  type: integer
                                  description: Alignment parameter
                                  examples:
                                    - 0
                              x-apidog-orders:
                                - word
                                - success
                                - startS
                                - endS
                                - palign
                              x-apidog-ignore-properties: []
                          waveformData:
                            type: array
                            description: Waveform data, used for audio visualization
                            items:
                              type: number
                            examples:
                              - - 0
                                - 1
                                - 0.5
                                - 0.75
                          hootCer:
                            type: number
                            description: Lyrics alignment accuracy score
                            examples:
                              - 0.3803191489361702
                          isStreamed:
                            type: boolean
                            description: Whether it's streaming audio
                            examples:
                              - false
                        x-apidog-orders:
                          - alignedWords
                          - waveformData
                          - hootCer
                          - isStreamed
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  alignedWords:
                    - word: |-
                        [Verse]
                        Waggin'
                      success: true
                      startS: 1.36
                      endS: 1.79
                      palign: 0
                  waveformData:
                    - 0
                    - 1
                    - 0.5
                    - 0.75
                  hootCer: 0.3803191489361702
                  isStreamed: false
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
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506290-run
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
