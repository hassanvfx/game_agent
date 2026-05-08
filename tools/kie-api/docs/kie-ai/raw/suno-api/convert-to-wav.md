# Convert to WAV Format

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/wav/generate:
    post:
      summary: Convert to WAV Format
      deprecated: false
      description: >-
        Convert an existing music track to high-quality WAV format.


        ### Usage Guide

        - Use this endpoint to obtain WAV format files from your generated music

        - WAV files provide uncompressed audio for professional editing and
        processing

        - Converted files maintain the full quality of the original audio


        ### Parameter Details

        - `taskId` identifies the original music generation task

        - `audioId` specifies which audio track to convert when multiple
        variations exist


        ### Developer Notes

        - Generated WAV files are retained for 14 days

        - WAV files are typically 5-10 times larger than MP3 equivalents

        - Processing time may vary depending on the length of the original audio
      operationId: convert-to-wav
      tags:
        - docs/en/Market/Suno API/WAV Conversion
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - callBackUrl
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
                    Unique identifier of the specific audio track to convert.
                    This ID is returned in the callback data after music
                    generation completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive WAV conversion task completion updates.
                    Required for all WAV conversion requests.


                    - System will POST task status and results to this URL when
                    WAV conversion completes

                    - Callback includes the high-quality WAV file download URL

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing the WAV file location

                    - For detailed callback format and implementation guide, see
                    [WAV Conversion
                    Callbacks](https://docs.kie.ai/suno-api/convert-to-wav-callbacks)

                    - Alternatively, use the Get WAV Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
              x-apidog-orders:
                - taskId
                - audioId
                - callBackUrl
              x-apidog-ignore-properties: []
            example:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
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
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request has been processed
                          successfully

                          - **400**: Format Error - The parameter is not in a
                          valid JSON format.

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

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request

                          Build Failed - Audio wav generation failed
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
        wavGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when WAV format audio generation
                is complete.


                ### Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "success",
                  "data": {
                    "audioWavUrl": "https://example.com/s/04e6****e727.wav",
                    "task_id": "988e****c8d3"
                  }
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
                                - 500
                              description: >-
                                Response status code


                                - **200**: Success - Request has been processed
                                successfully

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
                          example: success
                        data:
                          type: object
                          properties:
                            task_id:
                              type: string
                              description: Task ID
                            audioWavUrl:
                              type: string
                              description: WAV format audio file URL
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Suno API/WAV Conversion
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506298-run
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
