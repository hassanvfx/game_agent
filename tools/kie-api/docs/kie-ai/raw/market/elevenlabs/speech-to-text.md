# elevenlabs/speech-to-text

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/jobs/createTask:
    post:
      summary: elevenlabs/speech-to-text
      deprecated: false
      description: >
        Content generation using elevenlabs/speech-to-text


        ## Query Task Status


        After submitting a task, use the unified query endpoint to check
        progress and retrieve results:


        <Card title="Get Task Details" icon="lucide-search"
        href="/market/common/get-task-detail">
          Learn how to query task status and retrieve generation results
        </Card>


        ::: tip[]

        For production use, we recommend using the `callBackUrl` parameter to
        receive automatic notifications when generation completes, rather than
        polling the status endpoint.

        :::


        ## Related Resources


        <CardGroup cols={3}>
          <Card title="Market Overview" icon="lucide-store" href="/market/quickstart">
            Explore all available models
          </Card>
          <Card title="File Upload API" icon="lucide-cog" href="/file-upload-api/quickstart">
            Learn how to upload and manage files
          </Card>
          <Card title="Common API" icon="lucide-webhook" href="/common-api/get-account-credits">
            Check credits and account usage
          </Card>
        </CardGroup>
      operationId: elevenlabs-speech-to-text
      tags:
        - docs/en/Market/Music Models/ElevenLabs
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - model
              properties:
                model:
                  type: string
                  enum:
                    - elevenlabs/speech-to-text
                  default: elevenlabs/speech-to-text
                  description: |-
                    The model name to use for generation. Required field.

                    - Must be `elevenlabs/speech-to-text` for this endpoint
                  examples:
                    - elevenlabs/speech-to-text
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive generation task completion updates.
                    Optional but recommended for production use.


                    - System will POST task status and results to this URL when
                    generation completes

                    - Callback includes generated content URLs and task
                    information

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing results

                    - Alternatively, use the Get Task Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://your-domain.com/api/callback
                input:
                  type: object
                  description: Input parameters for the generation task
                  properties:
                    audio_url:
                      description: >-
                        URL of the audio file to transcribe (File URL after
                        upload, not file content; Accepted types: audio/mpeg,
                        audio/wav, audio/x-wav, audio/aac, audio/mp3, audio/ogg;
                        Max size: 200.0MB)
                      type: string
                      examples:
                        - >-
                          https://file.aiquickdraw.com/custom-page/akr/section-images/1757157053357tn37vxc8.mp3
                    language_code:
                      description: 'Language code of the audio (Max length: 500 characters)'
                      type: string
                      maxLength: 500
                      examples:
                        - ''
                    tag_audio_events:
                      description: >-
                        Tag audio events like laughter, applause, etc. (Boolean
                        value (true/false))
                      type: boolean
                      examples:
                        - true
                    diarize:
                      description: >-
                        Whether to annotate who is speaking (Boolean value
                        (true/false))
                      type: boolean
                      examples:
                        - true
                  required:
                    - audio_url
                  x-apidog-orders:
                    - audio_url
                    - language_code
                    - tag_audio_events
                    - diarize
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: elevenlabs/speech-to-text
              callBackUrl: https://your-domain.com/api/callback
              input:
                audio_url: >-
                  https://file.aiquickdraw.com/custom-page/akr/section-images/1757157053357tn37vxc8.mp3
                language_code: ''
                tag_audio_events: true
                diarize: true
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponseWithRecordId'
              example:
                code: 200
                msg: success
                data:
                  taskId: task_elevenlabs_1765185413162
                  recordId: record_elevenlabs_1765185413162
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
      x-apidog-folder: docs/en/Market/Music Models/ElevenLabs
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506429-run
components:
  schemas:
    ApiResponseWithRecordId:
      type: object
      properties:
        code:
          type: integer
          enum:
            - 200
            - 401
            - 402
            - 404
            - 422
            - 429
            - 455
            - 500
            - 501
            - 505
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

            - **455**: Service Unavailable - System is currently undergoing
            maintenance

            - **500**: Server Error - An unexpected error occurred while
            processing the request

            - **501**: Generation Failed - Content generation task failed

            - **505**: Feature Disabled - The requested feature is currently
            disabled
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
            recordId:
              type: string
              description: Record ID, can be used to get the record details
          x-apidog-orders:
            - taskId
            - recordId
          x-apidog-ignore-properties: []
      x-apidog-orders:
        - code
        - msg
        - data
      title: response with recordId
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
