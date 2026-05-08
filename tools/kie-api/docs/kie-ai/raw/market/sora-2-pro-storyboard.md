# Sora2 - Pro Storyboard

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
      summary: Sora2 - Pro Storyboard
      deprecated: false
      description: >-
        Video generation using sora-2-pro-storyboard


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
      operationId: sora-2-pro-storyboard
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
                    - sora-2-pro-storyboard
                  default: sora-2-pro-storyboard
                  description: |-
                    The model name to use for generation. Required field.

                    - Must be `sora-2-pro-storyboard` for this endpoint
                  examples:
                    - sora-2-pro-storyboard
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
                    shots:
                      description: >-
                        Array of shot descriptions with durations. Total
                        duration of all shots cannot exceed the selected
                        n_frames value.
                      type: array
                      items:
                        type: object
                        properties:
                          Scene:
                            type: string
                            description: Detailed description of the scene/shot
                            examples:
                              - >-
                                A cute fluffy orange-and-white kitten wearing
                                orange headphones, sitting at a cozy indoor
                                table with a small slice of cake on a plate, a
                                toy fish and a silver microphone nearby, warm
                                soft lighting, cinematic close-up, shallow depth
                                of field, gentle ASMR atmosphere.
                          duration:
                            type: number
                            description: >-
                              Duration of this shot in seconds. Total duration
                              of all shots cannot exceed n_frames.
                            minimum: 0.1
                            maximum: 15
                            examples:
                              - 7.5
                        required:
                          - Scene
                          - duration
                        x-apidog-orders:
                          - Scene
                          - duration
                        x-apidog-ignore-properties: []
                      minItems: 1
                      maxItems: 10
                      examples:
                        - - Scene: >-
                              A cute fluffy orange-and-white kitten wearing
                              orange headphones, sitting at a cozy indoor table
                              with a small slice of cake on a plate, a toy fish
                              and a silver microphone nearby, warm soft
                              lighting, cinematic close-up, shallow depth of
                              field, gentle ASMR atmosphere.
                            duration: 7.5
                          - Scene: >-
                              The same cute fluffy orange-and-white kitten
                              wearing orange headphones, in the same cozy indoor
                              ASMR setup with the toy fish and microphone, the
                              cake now finished, the kitten gently licks its
                              lips with a satisfied smile, warm ambient
                              lighting, cinematic close-up, shallow depth of
                              field, calm and content mood.
                            duration: 7.5
                    n_frames:
                      description: Total length of the video
                      type: string
                      enum:
                        - '10'
                        - '15'
                        - '25'
                      default: '15'
                      examples:
                        - '15'
                    image_urls:
                      description: >-
                        Upload an image file to use as input for the API (File
                        URL after upload, not file content; Accepted types:
                        image/jpeg, image/png, image/webp; Max size: 10.0MB).
                        Limited to exactly 1 image.
                      type: array
                      items:
                        type: string
                        format: uri
                      minItems: 1
                      maxItems: 1
                      examples:
                        - - >-
                            https://file.aiquickdraw.com/custom-page/akr/section-images/1760776438785hyue5ogz.png
                    aspect_ratio:
                      description: This parameter defines the aspect ratio of the image.
                      type: string
                      enum:
                        - portrait
                        - landscape
                      default: landscape
                      examples:
                        - landscape
                    upload_method:
                      type: string
                      description: >-
                        Upload destination. Defaults to s3; choose oss for
                        Aliyun storage (better access within China).
                      enum:
                        - s3
                        - oss
                      x-apidog-enum:
                        - value: s3
                          name: ''
                          description: ''
                        - value: oss
                          name: ''
                          description: ''
                  x-apidog-orders:
                    - shots
                    - n_frames
                    - image_urls
                    - aspect_ratio
                    - upload_method
                    - 01KH0FG3QMQV42KBJHG2PZQVNE
                  x-apidog-refs:
                    01KH0FG3QMQV42KBJHG2PZQVNE:
                      type: object
                      properties: {}
                  required:
                    - upload_method
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-2-pro-storyboard
              callBackUrl: https://your-domain.com/api/callback
              input:
                n_frames: '15'
                image_urls:
                  - >-
                    https://file.aiquickdraw.com/custom-page/akr/section-images/1760776438785hyue5ogz.png
                aspect_ratio: landscape
                upload_method: s3
                shots:
                  - Scene: >-
                      A cute fluffy orange-and-white kitten wearing orange
                      headphones, sitting at a cozy indoor table with a small
                      slice of cake on a plate, a toy fish and a silver
                      microphone nearby, warm soft lighting, cinematic close-up,
                      shallow depth of field, gentle ASMR atmosphere.
                    duration: 7.5
                  - Scene: >-
                      The same cute fluffy orange-and-white kitten wearing
                      orange headphones, in the same cozy indoor ASMR setup with
                      the toy fish and microphone, the cake now finished, the
                      kitten gently licks its lips with a satisfied smile, warm
                      ambient lighting, cinematic close-up, shallow depth of
                      field, calm and content mood.
                    duration: 7.5
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
                  taskId: task_sora-2-pro-storyboard_1765188271139
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506415-run
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
