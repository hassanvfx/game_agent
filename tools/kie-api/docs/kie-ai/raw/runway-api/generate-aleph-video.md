# Generate Aleph Video

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/aleph/generate:
    post:
      summary: Generate Aleph Video
      deprecated: false
      description: >-
        > Using Runway Aleph model for video-to-video conversion to create
        dynamic AI-generated videos


        ## Overview


        Transform existing videos into enhanced dynamic content using Runway's
        advanced Aleph AI model. This endpoint enables precise video-to-video
        generation through text-guided transformations, perfect for creating
        enhanced visual content from existing videos.


        :::highlight purple

        The Runway Aleph API requires a text prompt and reference video URL to
        generate transformed videos. The AI will modify and enhance the provided
        video based on your text description.

        :::
      operationId: generate-aleph-video
      tags:
        - docs/en/Market/Video Models/Runway API/Aleph
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - prompt
                - videoUrl
              properties:
                prompt:
                  type: string
                  description: >-
                    Descriptive text that guides the AI video generation. Be
                    specific about subject, action, style, and setting.
                    Describes how to animate or modify the reference image
                    content.
                  examples:
                    - >-
                      A majestic eagle soaring through mountain clouds at sunset
                      with cinematic camera movement
                videoUrl:
                  type: string
                  description: >-
                    Reference video URL to base the video-to-video generation
                    on. The AI will transform and enhance this video according
                    to the prompt.
                  examples:
                    - https://example.com/input-video.mp4
                callBackUrl:
                  type: string
                  description: >-
                    The URL to receive AI video generation task completion
                    updates.


                    - System will POST task status and results to this URL when
                    video generation completes

                    - Callback includes generated video URLs, cover images, and
                    task information

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing video results

                    - For detailed callback format and implementation guide, see
                    [Aleph Video Generation
                    Callbacks](https://docs.kie.ai/runway-api/generate-aleph-video-callbacks)

                    - Alternatively, use the Get Aleph Video Details endpoint to
                    poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
                waterMark:
                  type: string
                  description: >-
                    Optional watermark text content. An empty string indicates
                    no watermark, while a non-empty string will display the
                    specified text as a watermark in the video.
                  examples:
                    - kie.ai
                uploadCn:
                  type: boolean
                  description: >-
                    Upload method selection. Default value is false (S3/R2), set
                    to true for Alibaba Cloud OSS upload, set to false for
                    overseas R2 server upload.
                  default: false
                  examples:
                    - false
                aspectRatio:
                  type: string
                  description: Video aspect ratio.
                  enum:
                    - '16:9'
                    - '9:16'
                    - '4:3'
                    - '3:4'
                    - '1:1'
                    - '21:9'
                  examples:
                    - '16:9'
                seed:
                  type: integer
                  description: Random seed. Set for reproducible generation.
                  examples:
                    - 123456
                referenceImage:
                  type: string
                  format: uri
                  description: >-
                    Reference image URL to influence the style or content of the
                    output.
                  examples:
                    - https://example.com/reference.jpg
              x-apidog-orders:
                - prompt
                - videoUrl
                - callBackUrl
                - waterMark
                - uploadCn
                - aspectRatio
                - seed
                - referenceImage
              x-apidog-ignore-properties: []
            example:
              prompt: >-
                A majestic eagle soaring through mountain clouds at sunset with
                cinematic camera movement
              videoUrl: https://example.com/input-video.mp4
              callBackUrl: https://api.example.com/callback
              waterMark: kie.ai
              uploadCn: false
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
                          failed validation checks.The request parameters are
                          incorrect, please check the parameters.

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
                            description: >-
                              Unique identifier for the generation task, can be
                              used with `Get Aleph Video Details` to query task
                              status
                            examples:
                              - ee603959-debb-48d1-98c4-a6d1c717eba6
                        x-apidog-orders:
                          - taskId
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  taskId: ee603959-debb-48d1-98c4-a6d1c717eba6
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
        onVideoGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: Aleph Video Generation Completion Callback
              description: >-
                When Aleph video generation is complete, the system will send a
                POST request to the provided callback URL to notify the result
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      type: object
                      required:
                        - code
                        - data
                        - msg
                      properties:
                        code:
                          type: integer
                          description: Status code, 200 indicates success
                          example: 200
                        msg:
                          type: string
                          description: Status message
                          example: All generated successfully.
                        data:
                          type: object
                          required:
                            - image_url
                            - task_id
                            - video_id
                            - video_url
                          properties:
                            image_url:
                              type: string
                              description: Cover image URL of the generated video
                              example: https://file.com/m/xxxxxxxx.png
                            task_id:
                              type: string
                              description: Task ID
                              example: ee603959-debb-48d1-98c4-a6d1c717eba6
                            video_id:
                              type: string
                              description: Video ID
                              example: 485da89c-7fca-4340-8c04-101025b2ae71
                            video_url:
                              type: string
                              description: Accessible video URL, valid for 14 days
                              example: https://file.com/k/xxxxxxx.mp4
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
                                  - 500
                                description: >-
                                  Response status code


                                  - **200**: Success - Request has been
                                  processed successfully

                                  - **400**: Inappropriate content detected.
                                  Please replace the image or video.

                                  Incorrect image format.

                                  Please try again later. You can upgrade to
                                  Standard membership to start generating now.

                                  Reached the limit for concurrent generations.

                                  Unsupported width or height. Please adjust the
                                  size and try again.

                                  Upload failed due to network reasons, please
                                  re-enter.

                                  Your prompt was caught by our AI moderator.
                                  Please adjust it and try again!

                                  Your prompt/negative prompt cannot exceed 2048
                                  characters. Please check if your input is too
                                  long.

                                  Your video creation prompt contains NSFW
                                  content, which isn't allowed under our policy.
                                  Kindly revise your prompt and generate again.

                                  - **500**: Server Error - An unexpected error
                                  occurred while processing the request
                              msg:
                                type: string
                                description: Error message when code != 200
                                example: success
                      example:
                        code: 200
                        msg: success
      x-apidog-folder: docs/en/Market/Video Models/Runway API/Aleph
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506236-run
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
