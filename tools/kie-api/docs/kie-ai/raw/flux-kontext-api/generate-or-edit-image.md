# Generate or Edit Image

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/flux/kontext/generate:
    post:
      summary: Generate or Edit Image
      deprecated: false
      description: >-
        Create a new image generation or editing task using the Flux Kontext AI
        model.


        ### Usage Modes

        1. **Text-to-Image Generation**
           - Provide `prompt` and `aspectRatio`
           - Model will generate a new image based on the text description

        2. **Image Editing**
           - Provide `prompt` and `inputImage`
           - You can optionally provide an `aspectRatio`.  
              - If supplied, the output will be cropped or padded to match this ratio.  
              - If omitted, the original image's ratio will be preserved.
           - Model will edit the input image according to the prompt

        ### Important Notes

        - Generated images will expire after 14 days

        - Prompts only support English

        - Choose the appropriate model based on your needs:
          - flux-kontext-pro: Standard model for most use cases
          - flux-kontext-max: Enhanced model for complex scenes
      operationId: generate-or-edit-image
      tags:
        - docs/en/Market/Image    Models/Flux Kontext API
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
                    Text prompt describing the desired image or edit. Required
                    for both generation and editing modes.


                    - Should be detailed and specific

                    - For image editing, describe the desired changes

                    - For image generation, describe the complete scene

                    - IMPORTANT: Only English language is supported
                  examples:
                    - >-
                      A serene mountain landscape at sunset with a lake
                      reflecting the orange sky
                enableTranslation:
                  type: boolean
                  description: >-
                    Whether to enable automatic translation feature.


                    - Since prompt only supports English, when this parameter is
                    true, the system will automatically translate non-English
                    prompts to English

                    - If your prompt is already in English, you can set this to
                    false

                    - Default value: true
                  examples:
                    - true
                uploadCn:
                  type: boolean
                  description: >-
                    (Optional) Specifies the server region for image upload. Set
                    to true to use servers in China, false to use non-China
                    servers. Choose based on your geographical location for
                    optimal upload speeds.
                  examples:
                    - false
                inputImage:
                  type: string
                  format: uri
                  description: >-
                    URL of the input image for editing mode. Required when
                    editing an existing image.


                    - Must be a valid image URL

                    - Image must be accessible to the API server
                  examples:
                    - https://example.com/input-image.jpg
                aspectRatio:
                  type: string
                  description: >-
                    Output image aspect ratio. You Applicable in both
                    text-to-image generation and image editing modes.


                    For **text-to-image generation** , the output image will
                    follow the specified aspect ratio.


                    For **image editing** , if aspectRatio is provided, the
                    edited image will follow that ratio. If not provided, the
                    image will retain its original aspect ratio.


                    Supported Aspect Ratios:


                    | Ratio | Format Type | Common Use Cases |

                    |-------|-------------|-----------------|

                    | 21:9  | Ultra-wide  | Cinematic displays, panoramic views
                    |

                    | 16:9  | Widescreen  | HD video, desktop wallpapers |

                    | 4:3   | Standard    | Traditional displays, presentations
                    |

                    | 1:1   | Square      | Social media posts, profile pictures
                    |

                    | 3:4   | Portrait    | Magazine layouts, portrait photos |

                    | 9:16  | Mobile Portrait | Smartphone wallpapers, stories |


                    > Note: Default ratio is "16:9" if not specified.
                  enum:
                    - '21:9'
                    - '16:9'
                    - '4:3'
                    - '1:1'
                    - '3:4'
                    - '9:16'
                  default: '16:9'
                outputFormat:
                  type: string
                  description: Output image format.
                  enum:
                    - jpeg
                    - png
                  default: jpeg
                promptUpsampling:
                  type: boolean
                  description: |-
                    - If true, performs upsampling on the prompt
                    - May increase processing time
                  default: false
                model:
                  type: string
                  description: >-
                    Model version to use for generation.


                    Available Options:


                    | Model | Description |

                    |--------------|-------------|

                    | flux-kontext-pro | Standard model with balanced
                    performance |

                    | flux-kontext-max | Enhanced model with advanced
                    capabilities |


                    > Note: Choose flux-kontext-max for more demanding tasks
                    that require higher quality and detail
                  enum:
                    - flux-kontext-pro
                    - flux-kontext-max
                  default: flux-kontext-pro
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive image generation or editing task
                    completion updates. Optional but recommended for production
                    use.


                    - System will POST task status and results to this URL when
                    image generation or editing completes

                    - Callback includes generated image URLs and task
                    information for both text-to-image and image editing
                    operations

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing image results

                    - For detailed callback format and implementation guide, see
                    [Image Generation/Editing
                    Callbacks](https://docs.kie.ai/flux-kontext-api/generate-or-edit-image-callbacks)

                    - Alternatively, use the Get Image Details endpoint to poll
                    task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://your-callback-url.com/callback
                safetyTolerance:
                  type: integer
                  description: >-
                    **For Image Generation Mode:**

                    Moderation level for inputs and outputs. Value ranges from 0
                    (most strict) to 6 (more permissive).


                    **For Image Editing Mode:**

                    Moderation level for inputs and outputs. Value ranges from 0
                    (most strict) to 2 (balanced).


                    Default: 2
                  enum:
                    - 0
                    - 1
                    - 2
                    - 3
                    - 4
                    - 5
                    - 6
                  default: 2
                  examples:
                    - 2
                watermark:
                  type: string
                  description: |-
                    Watermark identifier to add to the generated image.

                    - Optional
                    - If provided, a watermark will be added to the output image
                  examples:
                    - your-watermark-id
              required:
                - prompt
              x-apidog-orders:
                - prompt
                - enableTranslation
                - uploadCn
                - inputImage
                - aspectRatio
                - outputFormat
                - promptUpsampling
                - model
                - callBackUrl
                - safetyTolerance
                - watermark
              examples:
                - prompt: >-
                    A serene mountain landscape at sunset with a lake reflecting
                    the orange sky
                  enableTranslation: true
                  aspectRatio: '16:9'
                  outputFormat: jpeg
                  promptUpsampling: false
                  model: flux-kontext-pro
              x-apidog-ignore-properties: []
            example:
              prompt: >-
                A serene mountain landscape at sunset with a lake reflecting the
                orange sky
              enableTranslation: true
              aspectRatio: '16:9'
              outputFormat: jpeg
              promptUpsampling: false
              model: flux-kontext-pro
              safetyTolerance: 2
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
                          - 422
                          - 429
                          - 455
                          - 500
                          - 501
                          - 505
                        description: >-
                          Response status code


                          - **200**: Success - Request has been processed
                          successfully

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist

                          - **422**: Validation Error - The request parameters
                          failed validation checks.The request parameters are
                          incorrect, please check the parameters.

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request

                          Server Error - The security tolerance level is out of
                          range and should be 0-2 or 0-6

                          - **501**: Generation Failed - Image generation task
                          failed

                          - **505**: Feature Disabled - The requested feature is
                          currently disabled
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
                              Task ID, can be used with Get Image Details
                              endpoint to query task status
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
        onImageGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: Image Generation Callback
              description: >-
                When the image generation task is completed, the system will
                send the result to your provided callback URL via POST request
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
                            Status code


                            - **200**: Success - Image generation completed
                            successfully

                            - **400**: Failed - Your prompt was flagged by
                            Website as violating content policies.

                            - **500**: Failed - Internal Error, Please try again
                            later.

                            - **501**: Failed - Image generation task failed
                          enum:
                            - 200
                            - 400
                            - 500
                            - 501
                        msg:
                          type: string
                          description: Status message
                          example: BFL image generated successfully.
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
                                originImageUrl:
                                  type: string
                                  description: Original image URL (valid for 10 minutes)
                                  example: https://example.com/original.jpg
                                resultImageUrl:
                                  type: string
                                  description: Generated image URL on our server
                                  example: https://example.com/result.jpg
                    example:
                      code: 200
                      msg: BFL image generated successfully.
                      data:
                        taskId: task12345
                        info:
                          originImageUrl: https://example.com/original.jpg
                          resultImageUrl: https://example.com/result.jpg
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Image    Models/Flux Kontext API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506240-run
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
