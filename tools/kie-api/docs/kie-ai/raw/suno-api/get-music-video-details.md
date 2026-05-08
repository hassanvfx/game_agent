# Get Music Video Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/mp4/record-info:
    get:
      summary: Get Music Video Details
      deprecated: false
      description: >-
        Retrieve detailed information about a music video generation task.


        ### Usage Guide

        - Use this endpoint to check the status of a video generation task

        - Access the video URL once generation is complete

        - Track processing progress and any errors that may have occurred


        ### Status Descriptions

        - `PENDING`: Task is waiting to be processed

        - `SUCCESS`: Video generation completed successfully

        - `CREATE_TASK_FAILED`: Failed to create the video generation task

        - `GENERATE_MP4_FAILED`: Failed during video file creation


        ### Developer Notes

        - The video URL is only available in the response when status is
        `SUCCESS`

        - Error codes and messages are provided for failed tasks

        - Videos are retained for 14 days after successful generation
      operationId: get-music-video-details
      tags:
        - docs/en/Market/Suno API/Music Video Generation
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the music video generation task to retrieve.
            This is the taskId returned when creating the music video generation
            task.
          required: true
          example: taskId_774b9aa0422f
          schema:
            type: string
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

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource

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
                      musicId:
                        type: string
                        description: Music ID
                        examples:
                          - ''
                      callbackUrl:
                        type: string
                        description: Callback URL
                        examples:
                          - ''
                      musicIndex:
                        type: integer
                        format: int32
                        description: Music index 0 or 1
                        examples:
                          - 0
                      completeTime:
                        type: string
                        format: date-time
                        description: Completion callback time
                        examples:
                          - ''
                      response:
                        type: object
                        description: Completion callback result
                        properties:
                          videoUrl:
                            type: string
                            description: Video URL
                            examples:
                              - ''
                        x-apidog-orders:
                          - videoUrl
                        x-apidog-ignore-properties: []
                      successFlag:
                        type: string
                        description: >-
                          PENDING-Waiting for execution SUCCESS-Success
                          CREATE_TASK_FAILED-Failed to create task
                          GENERATE_MP4_FAILED-Failed to generate MP4
                        examples:
                          - ''
                      createTime:
                        type: string
                        format: date-time
                        description: Creation time
                        examples:
                          - ''
                      errorCode:
                        type: integer
                        format: int32
                        description: >-
                          Error code


                          - **200**: Success - Request has been processed
                          successfully

                          - **500**: Internal Error - Please try again later.
                        enum:
                          - 200
                          - 500
                        examples:
                          - 0
                      errorMessage:
                        type: string
                        description: Error message
                        examples:
                          - ''
                    x-apidog-orders:
                      - taskId
                      - musicId
                      - callbackUrl
                      - musicIndex
                      - completeTime
                      - response
                      - successFlag
                      - createTime
                      - errorCode
                      - errorMessage
                    x-apidog-ignore-properties: []
                x-apidog-orders:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  taskId: 988e****c8d3
                  musicId: e231****-****-****-****-****8cadc7dc
                  callbackUrl: https://api.example.com/callback
                  musicIndex: 0
                  completeTime: '2025-01-01 00:10:00'
                  response:
                    videoUrl: https://example.com/s/04e6****e727.mp4
                  successFlag: SUCCESS
                  createTime: '2025-01-01 00:00:00'
                  errorCode: null
                  errorMessage: null
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
      x-apidog-folder: docs/en/Market/Suno API/Music Video Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506305-run
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
