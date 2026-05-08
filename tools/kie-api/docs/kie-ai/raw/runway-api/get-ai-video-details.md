# Get AI Video Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/runway/record-detail:
    get:
      summary: Get AI Video Details
      deprecated: false
      description: >-
        Retrieve comprehensive information about an AI-generated video task.


        ### Usage Guide

        - Check the status of a video generation or extension task

        - Access video URLs when generation is complete

        - Troubleshoot failed generation attempts


        ### Status Descriptions

        - `wait`: Task has been submitted but not yet queued

        - `queueing`: Task is waiting in processing queue

        - `generating`: Video generation is in progress

        - `success`: Video has been successfully generated

        - `fail`: Video generation has failed


        ### Developer Notes

        - Works with both standard video generation and video extension tasks

        - For extension tasks, the `parentTaskId` field identifies the original
        video

        - Video links are valid for 14 days, after which `expireFlag` will be
        set to 1
      operationId: get-ai-video-details
      tags:
        - docs/en/Market/Video Models/Runway API
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the video generation or extension task. This is
            the taskId returned when creating or extending an AI video.
          required: true
          example: ee603959-debb-48d1-98c4-a6d1c717eba6
          schema:
            type: string
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
                        description: Status message
                        examples:
                          - success
                      data:
                        type: object
                        properties:
                          taskId:
                            type: string
                            description: Unique identifier of the AI video generation task
                            examples:
                              - ee603959-debb-48d1-98c4-a6d1c717eba6
                          parentTaskId:
                            type: string
                            description: >-
                              For extension tasks only - the task ID of the
                              original video being extended. Empty for standard
                              generation tasks.
                            examples:
                              - ''
                          generateParam:
                            type: object
                            description: Parameters used for video generation or extension
                            properties:
                              prompt:
                                type: string
                                description: >-
                                  Text prompt used to guide the AI video
                                  generation
                                examples:
                                  - >-
                                    A fluffy orange cat dancing energetically in
                                    a colorful room with disco lights
                              imageUrl:
                                type: string
                                description: >-
                                  Reference image URL used for video generation
                                  or the frame from which extension began
                                examples:
                                  - https://example.com/image.jpg
                              expandPrompt:
                                type: boolean
                                description: >-
                                  Whether AI-powered prompt enhancement was used
                                  during generation
                                examples:
                                  - true
                            x-apidog-orders:
                              - prompt
                              - imageUrl
                              - expandPrompt
                            x-apidog-ignore-properties: []
                          state:
                            type: string
                            description: Current status of the video generation process
                            enum:
                              - wait
                              - queueing
                              - generating
                              - success
                              - fail
                            examples:
                              - success
                          generateTime:
                            type: string
                            description: Timestamp when the video generation was completed
                            examples:
                              - '2023-08-15 14:30:45'
                          videoInfo:
                            type: object
                            description: >-
                              Details about the generated video, available when
                              state is 'success'
                            properties:
                              videoId:
                                type: string
                                description: Unique identifier for the generated video file
                                examples:
                                  - 485da89c-7fca-4340-8c04-101025b2ae71
                              taskId:
                                type: string
                                description: >-
                                  The task ID associated with this video
                                  generation
                                examples:
                                  - ee603959-debb-48d1-98c4-a6d1c717eba6
                              videoUrl:
                                type: string
                                description: >-
                                  URL to access and download the generated
                                  video, valid for 14 days
                                examples:
                                  - https://file.com/k/xxxxxxx.mp4
                              imageUrl:
                                type: string
                                description: >-
                                  URL of a thumbnail image from the generated
                                  video
                                examples:
                                  - https://file.com/m/xxxxxxxx.png
                            x-apidog-orders:
                              - videoId
                              - taskId
                              - videoUrl
                              - imageUrl
                            x-apidog-ignore-properties: []
                          failCode:
                            type: integer
                            format: int32
                            description: >-
                              Error code


                              - **400**: Detected inappropriate content, please
                              try replacing the video.

                              HD quality free trials complete. Subscribe now to
                              continue creating in high resolution.

                              Inappropriate content detected. Please replace the
                              image or video.

                              Please try again later. You can upgrade to
                              Standard membership to start generating now.

                              Reached the limit for concurrent generations.

                              Unsupported width or height. Please adjust the
                              size and try again.

                              Upload failed due to network reasons, please
                              re-enter

                              Your prompt was caught by our AI moderator.

                              Your prompt has triggered our AI moderator, please
                              re-enter your prompt

                              Your prompt/negative prompt cannot exceed 2048
                              characters. Please check if your input is too
                              long.

                              Your video creation prompt contains NSFW content,
                              which isn't allowed under our policy. Kindly
                              revise your prompt and generate again.

                              Incorrect image format
                            enum:
                              - 400
                          failMsg:
                            type: string
                            description: >-
                              Detailed error message explaining the reason for
                              failure
                            examples:
                              - Generation failed, please try again later
                          expireFlag:
                            type: integer
                            format: int32
                            description: >-
                              Indicates if the video has expired: 0 = active
                              (still available), 1 = expired (no longer
                              available)
                            enum:
                              - 0
                              - 1
                            examples:
                              - 0
                        x-apidog-orders:
                          - taskId
                          - parentTaskId
                          - generateParam
                          - state
                          - generateTime
                          - videoInfo
                          - failCode
                          - failMsg
                          - expireFlag
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - code
                      - msg
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
      x-apidog-folder: docs/en/Market/Video Models/Runway API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506234-run
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
