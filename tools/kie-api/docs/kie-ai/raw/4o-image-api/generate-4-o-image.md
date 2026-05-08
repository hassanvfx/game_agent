# Generate 4o Image

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/gpt4o-image/generate:
    post:
      summary: Generate 4o Image
      deprecated: false
      description: >-
        Create a new 4o Image generation task. Generated images are stored for
        14 days, after which they expire.
      operationId: generate-4o-image
      tags:
        - docs/en/Market/Image    Models/4o Image API
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                prompt:
                  type: string
                  description: >-
                    (Optional) Text prompt that conveys the creative idea you
                    want the 4o model to render. Required if neither `filesUrl`
                    nor `fileUrl` is supplied. At least one of `prompt` or
                    `filesUrl` must be provided.
                  examples:
                    - A beautiful sunset over the mountains
                filesUrl:
                  type: array
                  items:
                    type: string
                    format: uri
                  description: >-
                    (Optional) Up to 5 publicly reachable image URLs to serve as
                    reference or source material. Use this when you want to edit
                    or build upon an existing picture. If you don’t have
                    reliable hosting, upload your images first via our File
                    Upload API quick‑start:
                    https://docs.kie.ai/file-upload-api/quickstart. Supported
                    formats: .jfif, .pjpeg, .jpeg, .pjp, .jpg, .png, .webp. At
                    least one of `prompt` or `filesUrl` must be provided.
                  examples:
                    - - https://example.com/image.png
                size:
                  type: string
                  description: >-
                    (Required) Aspect ratio of the generated image. Must be one
                    of the listed values.
                  enum:
                    - '1:1'
                    - '3:2'
                    - '2:3'
                  examples:
                    - '1:1'
                maskUrl:
                  type: string
                  format: uri
                  description: >-
                    (Optional) Mask image URL indicating areas to modify (black)
                    versus preserve (white). The mask must match the reference
                    image’s dimensions and format (≤ 25 MB). When more than one
                    image is supplied in `filesUrl`, `maskUrl` is ignored.


                    Example:

                    ![Mask
                    Example](https://static.aiquickdraw.com/images/docs/4o-gen-image-mask.png)


                    In the image above, the left side shows the original image,
                    the middle shows the mask image (white areas indicate parts
                    to be preserved, black areas indicate parts to be modified),
                    and the right side shows the final generated image.
                  examples:
                    - https://example.com/mask.png
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive 4o image generation task completion
                    updates. Optional but recommended for production use.


                    - System will POST task status and results to this URL when
                    4o image generation completes

                    - Callback includes generated image URLs and task
                    information for all variations

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing image generation results

                    - For detailed callback format and implementation guide, see
                    [4o Image Generation
                    Callbacks](https://docs.kie.ai/4o-image-api/generate-4-o-image-callbacks)

                    - Alternatively, use the Get 4o Image Details endpoint to
                    poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://your-callback-url.com/callback
                isEnhance:
                  type: boolean
                  description: >-
                    (Optional) Enable prompt enhancement for more refined
                    outputs in specialised scenarios (e.g., 3D renders).
                    Default false.
                  examples:
                    - false
                uploadCn:
                  type: boolean
                  description: >-
                    (Optional) Choose the upload region. `true` routes uploads
                    via China servers; `false` via non‑China servers.
                  examples:
                    - false
                enableFallback:
                  type: boolean
                  description: >-
                    (Optional) Activate automatic fallback to backup models
                    (e.g., Flux) if GPT‑4o image generation is unavailable.
                    Default false.
                  examples:
                    - false
                fallbackModel:
                  type: string
                  description: >-
                    (Optional) Specify which backup model to use when the main
                    model is unavailable. Takes effect when enableFallback is
                    true. Available values: GPT_IMAGE_1  or FLUX_MAX. Default
                    value is FLUX_MAX.
                  enum:
                    - GPT_IMAGE_1
                    - FLUX_MAX
                  default: FLUX_MAX
                  examples:
                    - FLUX_MAX
                fileUrl:
                  type: string
                  format: uri
                  description: >-
                    (Optional, Deprecated) File URL, such as an image URL. If
                    fileUrl is provided, 4o image may create based on this
                    image. This parameter will be deprecated in the future,
                    please use filesUrl instead.
                  deprecated: true
                  examples:
                    - https://example.com/image.png
              required:
                - size
              x-apidog-orders:
                - prompt
                - filesUrl
                - size
                - maskUrl
                - callBackUrl
                - isEnhance
                - uploadCn
                - enableFallback
                - fallbackModel
                - fileUrl
              examples:
                - filesUrl:
                    - https://example.com/image.png
                  prompt: A beautiful sunset over the mountains
                  size: '1:1'
                  callBackUrl: https://your-callback-url.com/callback
                  isEnhance: false
                  uploadCn: false
                  enableFallback: false
                  fallbackModel: FLUX_MAX
              x-apidog-ignore-properties: []
            example:
              filesUrl:
                - https://example.com/image.png
              prompt: A beautiful sunset over the mountains
              size: '1:1'
              callBackUrl: https://your-callback-url.com/callback
              isEnhance: false
              uploadCn: false
              enableFallback: false
              fallbackModel: FLUX_MAX
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
                          - 422
                          - 429
                          - 455
                          - 500
                          - 550
                        description: >-
                          Response Status Codes


                          - **200**: Success - Request has been processed
                          successfully  

                          - **400**: Format Error - The parameter is not in a
                          valid JSON format  

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid  

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation  

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist  

                          - **422**: Validation Error - The request parameters
                          failed validation checks  

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource  

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance  

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request  
                            - Build Failed - vocal removal generation failed  
                          - **550**: Connection Denied - Task was rejected due
                          to a full queue, likely caused by source site's
                          issues. Please contact the administrator to confirm.
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
                              Task ID, can be used with [Get 4o Image
                              Details](/4o-image-api/get-4-o-image-details) to
                              query task status
                            examples:
                              - task12345
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
                  taskId: task12345
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
        on4oImageGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: 4o Image Generation Task Callback
              description: >-
                When the 4o Image task is completed, the system will send the
                result to your provided callback URL via POST request
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        code:
                          type: integer
                          description: >-
                            Response Status Codes


                            - **200**: Success - Image generation completed
                            successfully  

                            - **400**: Bad Request  
                              - The image content in filesUrl violates content policy  
                              - Image size exceeds maximum of 26214400 bytes  
                              - We couldn't process the provided image file (code=invalid_image_format)  
                              - Your content was flagged by OpenAI as violating content policies  
                            - **451**: Download Failed - Unable to download
                            image from the provided filesUrl  

                            - **500**: Server Error  
                              - Please try again later  
                              - Failed to get user token  
                              - Failed to generate image  
                              - GPT 4O failed to edit the picture  
                              - null
                          enum:
                            - 200
                            - 400
                            - 451
                            - 500
                        msg:
                          type: string
                          description: Status message
                          example: success
                        data:
                          type: object
                          properties:
                            taskId:
                              type: string
                              description: Task ID
                              example: task12345
                            info:
                              type: object
                              properties:
                                result_urls:
                                  type: array
                                  items:
                                    type: string
                                  description: List of generated image URLs
                                  example:
                                    - https://example.com/result/image1.png
                    example:
                      code: 200
                      msg: success
                      data:
                        taskId: task12345
                        info:
                          result_urls:
                            - https://example.com/result/image1.png
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Image    Models/4o Image API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506278-run
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
