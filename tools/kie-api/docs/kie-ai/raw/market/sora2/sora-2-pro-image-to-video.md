# Sora2 - Pro Image to Video

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
      summary: Sora2 - Pro Image to Video
      deprecated: false
      description: >-
        Transform images into dynamic videos powered by
        Sora-2-pro-image-to-video's advanced AI model


        ## Character Animation Integration


        For enhanced character animation capabilities, you can use the
        `character_id_list` parameter to reference pre-animated characters:


        <Card title="Sora2 - Characters" href="/market/sora2/sora-2-characters">
           Learn how to create character animations and get character_id_list for integration
        </Card>


        The `character_id_list` parameter is optional and allows you to
        incorporate multiple character animations (as an array, maximum 5) into
        your pro image-to-video generation.


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


        <CardGroup cols={2}>
          <Card title="Market Overview" icon="lucide-store" href="/market/quickstart">
            Explore all available models
          </Card>
          <Card title="Common API" icon="lucide-cog" href="/common-api/get-account-credits">
            Check credits and account usage
          </Card>
        </CardGroup>
      operationId: sora-2-pro-image-to-video
      tags:
        - docs/en/Market/Video Models/Sora2
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
                    - sora-2-pro-image-to-video
                  default: sora-2-pro-image-to-video
                  description: |-
                    The model name to use for generation. Required field.

                    - Must be `sora-2-pro-image-to-video` for this endpoint
                  examples:
                    - sora-2-pro-image-to-video
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
                progressCallBackUrl:
                  type: string
                  description: >-
                    User progress callback address

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  format: uri
                  examples:
                    - https://your-domain.com/api/v1/jobs/progressCallBackUrl
                input:
                  type: object
                  description: Input parameters for the generation task
                  properties:
                    prompt:
                      description: >-
                        The text prompt describing the desired video motion (Max
                        length: 10000 characters)
                      type: string
                      maxLength: 10000
                      examples:
                        - ''
                    image_urls:
                      description: >-
                        URL of the image to use as the first frame. Must be
                        publicly accessible (File URL after upload, not file
                        content; Accepted types: image/jpeg, image/png,
                        image/webp; Max size: 10.0MB)
                      type: array
                      items:
                        type: string
                        format: uri
                      maxItems: 1
                      examples:
                        - []
                    aspect_ratio:
                      description: This parameter defines the aspect ratio of the image.
                      type: string
                      enum:
                        - portrait
                        - landscape
                      default: landscape
                      examples:
                        - landscape
                    n_frames:
                      description: The number of frames to be generated.
                      type: string
                      enum:
                        - '10'
                        - '15'
                      default: '10'
                      examples:
                        - '10'
                    size:
                      description: The quality or size of the generated image.
                      type: string
                      enum:
                        - standard
                        - high
                      default: standard
                      examples:
                        - standard
                    remove_watermark:
                      description: >-
                        When enabled, removes watermarks from the generated
                        video. (Boolean value (true/false))
                      type: boolean
                      examples:
                        - true
                    character_id_list:
                      description: >-
                        Optional array of character IDs from Sora-2-characters
                        model to incorporate character animations into the video
                        generation. Maximum 5 character IDs allowed. Leave empty
                        if not using character animations.
                      type: array
                      items:
                        type: string
                      maxItems: 5
                      examples:
                        - - example_123456789
                          - example_987654321
                    upload_method:
                      type: string
                      description: >-
                        Upload destination. Defaults to s3; choose oss for
                        Aliyun storage (better access within China).
                      enum:
                        - oss
                        - s3
                      x-apidog-enum:
                        - value: oss
                          name: ''
                          description: ''
                        - value: s3
                          name: ''
                          description: ''
                      default: s3
                  required:
                    - prompt
                    - image_urls
                    - upload_method
                  x-apidog-orders:
                    - prompt
                    - image_urls
                    - aspect_ratio
                    - n_frames
                    - size
                    - remove_watermark
                    - character_id_list
                    - upload_method
                    - 01KH0FF8M78NHA5MW6PRWPAKCG
                  x-apidog-refs:
                    01KH0FF8M78NHA5MW6PRWPAKCG:
                      type: object
                      properties: {}
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - progressCallBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-2-pro-image-to-video
              callBackUrl: https://your-domain.com/api/callback
              progressCallBackUrl: https://your-domain.com/api/v1/jobs/progressCallBackUrl
              input:
                prompt: ''
                image_urls: []
                aspect_ratio: landscape
                n_frames: '10'
                size: standard
                remove_watermark: true
                upload_method: s3
                character_id_list:
                  - example_123456789
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
              example:
                code: 200
                msg: success
                data:
                  taskId: task_sora-2-pro-image-to-video_1765183474472
          headers: {}
          x-apidog-name: ''
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
      x-apidog-folder: docs/en/Market/Video Models/Sora2
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506411-run
components:
  schemas:
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
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

            - **433**: Request Limit - Sub-key Usage Exceeds Limit

            - **455**: Service Unavailable - System is currently undergoing
            maintenance

            - **500**: Server Error - An unexpected error occurred while
            processing the request

            - **501**: Generation Failed - Content generation task failed

            - **505**: Feature Disabled - The requested feature is currently
            disabled
          enum:
            - 200
            - 401
            - 402
            - 404
            - 422
            - 429
            - 433
            - 455
            - 500
            - 501
            - 505
          x-apidog-enum:
            - value: 200
              name: ''
              description: ''
            - value: 401
              name: ''
              description: ''
            - value: 402
              name: ''
              description: ''
            - value: 404
              name: ''
              description: ''
            - value: 422
              name: ''
              description: ''
            - value: 429
              name: ''
              description: ''
            - value: 433
              name: ''
              description: ''
            - value: 455
              name: ''
              description: ''
            - value: 500
              name: ''
              description: ''
            - value: 501
              name: ''
              description: ''
            - value: 505
              name: ''
              description: ''
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
          x-apidog-orders:
            - taskId
          required:
            - taskId
          x-apidog-ignore-properties: []
      x-apidog-orders:
        - code
        - msg
        - data
      title: response not with recordId
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
