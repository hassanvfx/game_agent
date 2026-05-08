# Create Music Video

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/mp4/generate:
    post:
      summary: Create Music Video
      deprecated: false
      description: >-
        Create a video with visualizations based on your generated music track.


        ### Usage Guide

        - Use this endpoint to turn your audio tracks into visually appealing
        videos

        - Add artist attribution and branding to your music videos

        - Videos can be shared on social media or embedded in websites


        ### Parameter Details

        - `taskId` identifies the original music generation task

        - `audioId` specifies which audio track to visualize when multiple
        variations exist

        - Optional `author` and `domainName` add customized branding to the
        video


        ### Developer Notes

        - Generated video files are retained for 14 days

        - Videos are optimized for social media sharing

        - Processing time varies based on audio length and server load
      operationId: create-music-video
      tags:
        - docs/en/Market/Suno API/Music Video Generation
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
                    - taskId_774b9aa0422f
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the specific audio track to visualize.
                    This ID is returned in the callback data after music
                    generation completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive music video generation task completion
                    updates. Required for all music video generation requests.


                    - System will POST task status and results to this URL when
                    video generation completes

                    - Callback includes the generated music video file URL with
                    visual effects and branding

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing the video file location

                    - For detailed callback format and implementation guide, see
                    [Music Video
                    Callbacks](https://docs.kie.ai/suno-api/create-music-video-callbacks)

                    - Alternatively, use the Get Music Video Details endpoint to
                    poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
                author:
                  type: string
                  maxLength: 50
                  description: >-
                    Artist or creator name to display as a signature on the
                    video cover. Maximum 50 characters. This creates attribution
                    for the music creator.
                  examples:
                    - DJ Electronic
                domainName:
                  type: string
                  maxLength: 50
                  description: >-
                    Website or brand to display as a watermark at the bottom of
                    the video. Maximum 50 characters. Useful for promotional
                    branding or attribution.
                  examples:
                    - music.example.com
              x-apidog-orders:
                - taskId
                - audioId
                - callBackUrl
                - author
                - domainName
              x-apidog-ignore-properties: []
            example:
              taskId: taskId_774b9aa0422f
              audioId: e231****-****-****-****-****8cadc7dc
              callBackUrl: https://api.example.com/callback
              author: DJ Electronic
              domainName: music.example.com
      responses:
        '200':
          description: Success
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
                          valid JSON format

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist

                          - **409**: Conflict - WAV record already exists

                          - **422**: Validation Error - The request parameters
                          failed validation checks

                          - **429**: Rate Limited - Your call frequency is too
                          high. Please try again later.

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request

                          Build Failed - Audio mp4 generation failed
                      msg:
                        type: string
                        description: Error message when code != 200
                        examples:
                          - success
                    x-apidog-orders:
                      - code
                      - msg
                    x-apidog-ignore-properties: []
                type: object
                properties:
                  code:
                    type: integer
                    format: int32
                    description: Status code
                    examples:
                      - 0
                  msg:
                    type: string
                    description: Status message
                    examples:
                      - ''
                  data:
                    type: object
                    properties:
                      taskId:
                        type: string
                        description: Task ID
                        examples:
                          - ''
                    x-apidog-orders:
                      - taskId
                    x-apidog-ignore-properties: []
                x-apidog-orders:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 0
                msg: ''
                data:
                  taskId: ''
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
        onMp4Generated:
          '{$request.body#/callBackUrl}':
            post:
              summary: MP4 Generation Completion Callback
              description: >-
                When MP4 generation is complete, the system will send a POST
                request to the provided callback URL to notify the result
              requestBody:
                required: true
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
                      type: object
                      required:
                        - code
                        - msg
                        - data
                      properties:
                        code:
                          type: integer
                          description: Status code, 0 indicates success
                          example: 0
                        msg:
                          type: string
                          description: Status message
                          example: msg_9a23a47664f7
                        data:
                          type: object
                          required:
                            - task_id
                            - video_url
                          properties:
                            task_id:
                              type: string
                              description: Unique identifier of the generation task
                              example: task_id_5bbe7721119d
                            video_url:
                              type: string
                              description: Accessible video URL, valid for 14 days
                              example: video_url_847715e66259
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Suno API/Music Video Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506304-run
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
