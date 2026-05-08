# Get Image Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/flux/kontext/record-info:
    get:
      summary: Get Image Details
      deprecated: false
      description: |-
        Query the status and results of an image generation or editing task.

        ### Status Descriptions
        - 0: GENERATING - Task is currently being processed
        - 1: SUCCESS - Task completed successfully
        - 2: CREATE_TASK_FAILED - Failed to create the task
        - 3: GENERATE_FAILED - Task creation succeeded but generation failed

        ### Important Notes
        - Generated images (resultImageUrl) will expire after 14 days
      operationId: get-image-details
      tags:
        - docs/en/Market/Image    Models/Flux Kontext API
      parameters:
        - name: taskId
          in: query
          description: Unique identifier of the image generation task
          required: true
          example: task12345
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
                          - 455
                          - 500
                          - 501
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

                          - **455**: Service Unavailable - System is currently
                          undergoing maintenance

                          - **500**: Server Error - An unexpected error occurred
                          while processing the request

                          - **501**: Generation Failed - Image generation task
                          failed
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
                            description: Unique identifier of the image generation task
                            examples:
                              - task12345
                          paramJson:
                            type: string
                            description: Request parameters in JSON format
                            examples:
                              - >-
                                {"prompt":"A serene mountain
                                landscape","aspectRatio":"16:9"}
                          completeTime:
                            type: string
                            format: date-time
                            description: Task completion time
                            examples:
                              - '2024-03-20T10:30:00Z'
                          response:
                            type: object
                            description: Final result
                            properties:
                              originImageUrl:
                                type: string
                                description: Original image URL (valid for 10 minutes)
                                examples:
                                  - https://example.com/original.jpg
                              resultImageUrl:
                                type: string
                                description: Generated image URL on our server
                                examples:
                                  - https://example.com/result.jpg
                            x-apidog-orders:
                              - originImageUrl
                              - resultImageUrl
                            x-apidog-ignore-properties: []
                          successFlag:
                            type: integer
                            description: Generation status flag
                            enum:
                              - 0
                              - 1
                              - 2
                              - 3
                            examples:
                              - 1
                          errorCode:
                            type: integer
                            description: >-
                              Error code if task failed


                              - **400**: Your prompt was flagged by Website as
                              violating content policies.

                              - **500**: Internal Error, Please try again later.

                              The security tolerance level is out of range and
                              should be 0-2 or 0-6.

                              - **501**: Image generation task failed
                            enum:
                              - 400
                              - 500
                              - 501
                            examples:
                              - null
                          errorMessage:
                            type: string
                            description: Error message if task failed
                            examples:
                              - ''
                          createTime:
                            type: string
                            format: date-time
                            description: Task creation time
                            examples:
                              - '2024-03-20T10:25:00Z'
                        x-apidog-orders:
                          - taskId
                          - paramJson
                          - completeTime
                          - response
                          - successFlag
                          - errorCode
                          - errorMessage
                          - createTime
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data:
                  taskId: task12345
                  paramJson: >-
                    {"prompt":"A serene mountain
                    landscape","aspectRatio":"16:9"}
                  completeTime: '2024-03-20T10:30:00Z'
                  response:
                    originImageUrl: https://example.com/original.jpg
                    resultImageUrl: https://example.com/result.jpg
                  successFlag: 1
                  errorCode: null
                  errorMessage: ''
                  createTime: '2024-03-20T10:25:00Z'
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
      x-apidog-folder: docs/en/Market/Image    Models/Flux Kontext API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506241-run
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
