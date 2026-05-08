# Get Cover Generation Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/suno/cover/record-info:
    get:
      summary: Get Cover Generation Details
      deprecated: false
      description: >-
        Get detailed information about Cover generation tasks.


        ### Usage Guide

        - Use this interface to check Cover generation task status

        - Access generated cover image URLs upon completion

        - Track processing progress and any errors that may occur


        ### Status Description

        - `PENDING`: Task awaiting processing

        - `SUCCESS`: Cover generation completed successfully

        - `CREATE_TASK_FAILED`: Cover generation task creation failed

        - `GENERATE_COVER_FAILED`: Cover image generation process failed


        ### Developer Notes

        - Cover image URLs are only available when status is `SUCCESS` in the
        response

        - Error codes and messages are provided for failed tasks

        - After successful generation, cover images are retained for 14 days
      operationId: get-cover-details
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the Cover generation task to retrieve. This is
            the taskId returned when creating the Cover generation task.
          required: true
          example: 21aee3c3c2a01fa5e030b3799fa4dd56
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


                          - **200**: Success - Request processed successfully

                          - **400**: Format error - Parameters are not in valid
                          JSON format

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account doesn't have
                          enough credits for this operation

                          - **404**: Not found - Requested resource or endpoint
                          doesn't exist

                          - **409**: Conflict - Cover record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limited - Request rate limit exceeded
                          for this resource

                          - **455**: Service unavailable - System currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request
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
                      - 200
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
                        description: Task ID
                        examples:
                          - 21aee3c3c2a01fa5e030b3799fa4dd56
                      parentTaskId:
                        type: string
                        description: Original music task ID
                        examples:
                          - 73d6128b3523a0079df10da9471017c8
                      callbackUrl:
                        type: string
                        description: Callback URL
                        examples:
                          - https://api.example.com/callback
                      completeTime:
                        type: string
                        format: date-time
                        description: Completion callback time
                        examples:
                          - '2025-01-15T10:35:27.000Z'
                      response:
                        type: object
                        description: Completion callback result
                        properties:
                          images:
                            type: array
                            items:
                              type: string
                            description: Cover image URL array
                            examples:
                              - - >-
                                  https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                                - >-
                                  https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                        x-apidog-orders:
                          - images
                        x-apidog-ignore-properties: []
                      successFlag:
                        type: integer
                        description: >-
                          Task status flag: 0-Pending, 1-Success, 2-Generating,
                          3-Generation failed
                        enum:
                          - 0
                          - 1
                          - 2
                          - 3
                        examples:
                          - 1
                      createTime:
                        type: string
                        format: date-time
                        description: Creation time
                        examples:
                          - '2025-01-15T10:33:01.000Z'
                      errorCode:
                        type: integer
                        format: int32
                        description: |-
                          Error code

                          - **200**: Success - Request processed successfully
                          - **500**: Internal error - Please try again later.
                        enum:
                          - 200
                          - 500
                        examples:
                          - 200
                      errorMessage:
                        type: string
                        description: Error message
                        examples:
                          - ''
                    x-apidog-orders:
                      - taskId
                      - parentTaskId
                      - callbackUrl
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
                  taskId: 21aee3c3c2a01fa5e030b3799fa4dd56
                  parentTaskId: 73d6128b3523a0079df10da9471017c8
                  callbackUrl: https://api.example.com/callback
                  completeTime: '2025-01-15T10:35:27.000Z'
                  response:
                    images:
                      - >-
                        https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                      - >-
                        https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
                  successFlag: 1
                  createTime: '2025-01-15T10:33:01.000Z'
                  errorCode: 200
                  errorMessage: ''
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
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506293-run
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
