# Sora2 - Characters Pro

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
      summary: Sora2 - Characters Pro
      deprecated: false
      description: >-
        > Create dynamic character animations from existing video tasks using
        Sora-2-characters-pro advanced AI model


        ## Prerequisites


        The Sora-2-characters-pro API generates character animations from an
        **existing video generation task**. You must have a completed task
        before using this API:


        1. **Complete a Video Generation Task**

           First, use one of the Sora video generation APIs (e.g., [Text to Video](./market/sora2/sora-2-text-to-video) or [Image to Video](./market/sora2/sora-2-image-to-video)) to create a video.

        2. **Obtain Task ID**

           After the video generation completes successfully, note the `taskId` from the response. This becomes your `origin_task_id`.

        3. **Specify Video Segment**

           Use the `timestamps` parameter to define which segment of the video to use. Format: `"x,y"` (e.g., `"3.55,5.55"`). The segment duration (y - x) must be between 1-4 seconds.

        4. **Submit Character Animation Task**

           Provide `origin_task_id`, `timestamps`, and `character_prompt` to generate character animations. Optionally include `character_user_name` to identify the character for reference.

        ## Parameter Reference


        | Parameter | Type | Required | Description |

        |:---|:---|:---|:---|

        | `origin_task_id` | string | Yes | Task ID of the original video
        generation task |

        | `timestamps` | string | Yes | Video segment time range. Format:
        `"x,y"` (e.g., `"3.55,5.55"`). Extracts segment from x to y seconds.
        Duration (y - x) must be 1-4 seconds |

        | `character_user_name` | string | No | Optional. Custom name for the
        character, used to identify and reference in subsequent operations. Max
        40 characters when provided |

        | `character_prompt` | string | Yes | Character persona prompt
        describing personality and appearance |

        | `safety_instruction` | string | No | Safety guidelines and content
        restrictions for the animation |


        :::caution


        **Timestamp Constraints**: The `timestamps` parameter must define a
        segment between 1-4 seconds. For example, `"3.55,5.55"` extracts a
        2-second segment. Invalid durations will cause processing errors.


        :::


        :::tip


        Use the [Get Task Details](/market/common/get-task-detail) endpoint to
        verify your original video task has completed successfully before
        submitting a character animation request.


        :::


        ## Query Task Status


        After submitting a task, use the unified query endpoint to check
        progress and retrieve results:


        <Card title="Get Task Details" icon="lucide-search"
        href="/market/common/get-task-detail">
           Learn how to query task status and retrieve generation results
        </Card>


        ### Task Query Response Format


        When the task is completed successfully (`state: "success"`), the
        `resultJson` field contains:


        ```json

        {
          "character_id": "example_123456789"
        }

        ```


        The `character_id` can be used to reference the generated character
        animation in subsequent operations.


        :::tip


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
      operationId: sora-2-characters-pro
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
                    - sora-2-characters-pro
                  default: sora-2-characters-pro
                  description: |-
                    The model name to use for generation. Required field.

                    - Must be `sora-2-characters-pro` for this endpoint
                  examples:
                    - sora-2-characters-pro
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
                    origin_task_id:
                      type: string
                      description: >-
                        Task ID of the original task. References a previously
                        completed video generation task.
                      examples:
                        - 7118f712c1f35c9b8bf2ad1af68ad482
                    timestamps:
                      type: string
                      description: >-
                        Enter the clip's start and end times in seconds. The
                        segment you select must be completely inside the
                        original video and between 1 s–4 s long; that slice will
                        be used as the character's training material.
                      examples:
                        - 3.55,5.55
                    character_user_name:
                      type: string
                      description: >-
                        Optional. Custom name for the character, used to
                        identify and reference the character in subsequent
                        operations. When provided, must be non-empty and max 40
                        characters.
                      maxLength: 40
                      examples:
                        - my_character_01
                    character_prompt:
                      type: string
                      description: >-
                        Character persona prompt. Required, non-empty. Describes
                        the character's personality and appearance.
                      maxLength: 5000
                      examples:
                        - >-
                          A friendly cartoon character with expressive eyes and
                          fluid movements
                    safety_instruction:
                      type: string
                      description: >-
                        Character safety instructions. Guidelines and content
                        restrictions for the animation.
                      maxLength: 5000
                      examples:
                        - >-
                          Ensure the animation is family-friendly and contains
                          no violent or inappropriate content
                  required:
                    - origin_task_id
                    - timestamps
                    - character_prompt
                  x-apidog-orders:
                    - origin_task_id
                    - timestamps
                    - character_user_name
                    - character_prompt
                    - safety_instruction
                  x-apidog-ignore-properties: []
              x-apidog-orders:
                - model
                - callBackUrl
                - input
              x-apidog-ignore-properties: []
            example:
              model: sora-2-characters-pro
              callBackUrl: https://your-domain.com/api/callback
              input:
                origin_task_id: 7118f712c1f35c9b8bf2ad1af68ad482
                timestamps: 3.55,5.55
                character_user_name: my_character_01
                character_prompt: >-
                  A friendly cartoon character with expressive eyes and fluid
                  movements
                safety_instruction: >-
                  Ensure the animation is family-friendly and contains no
                  violent or inappropriate content
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/ApiResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: >-
                              Task ID, can be used with Get Task Details
                              endpoint to query task status
                            examples:
                              - 7118f712c1f35c9b8bf2ad1af68ad482
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
                  taskId: task_sora-2-characters-pro_1765174270120
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
      x-apidog-folder: docs/en/Market/Video Models/Sora2
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28560562-run
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
