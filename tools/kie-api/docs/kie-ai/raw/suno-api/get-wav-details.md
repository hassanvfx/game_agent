# Get WAV Conversion Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/wav/record-info:
    get:
      summary: Get WAV Conversion Details
      deprecated: false
      description: >-
        Retrieve detailed information about a WAV format conversion task.


        ### Usage Guide

        - Use this endpoint to check the status of a WAV conversion task

        - Access the WAV file URL once conversion is complete

        - Track conversion progress and any errors that may have occurred


        ### Status Descriptions

        - `PENDING`: Task is waiting to be processed

        - `SUCCESS`: WAV conversion completed successfully

        - `CREATE_TASK_FAILED`: Failed to create the conversion task

        - `GENERATE_WAV_FAILED`: Failed during WAV file generation

        - `CALLBACK_EXCEPTION`: Error occurred during callback


        ### Developer Notes

        - The WAV file URL is only available in the response when status is
        `SUCCESS`

        - Error codes and messages are provided for failed tasks

        - WAV files are retained for 14 days after successful conversion
      operationId: get-wav-details
      tags:
        - docs/en/Market/Suno API/WAV Conversion
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the WAV conversion task to retrieve. This is
            the taskId returned when creating the WAV conversion task.
          required: true
          example: 988e****c8d3
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

                          - **451**: Failed to fetch the image. Kindly verify
                          any access limits set by you or your service provider.

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
                            description: Task ID
                          musicId:
                            type: string
                            description: Music ID
                          callbackUrl:
                            type: string
                            description: Callback address
                          musicIndex:
                            type: integer
                            description: Music index 0 or 1
                          completeTime:
                            type: string
                            description: Complete callback time
                            format: date-time
                          response:
                            type: object
                            properties:
                              audioWavUrl:
                                type: string
                                description: WAV format audio file URL
                            x-apidog-orders:
                              - audioWavUrl
                            x-apidog-ignore-properties: []
                          successFlag:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_WAV_FAILED
                              - CALLBACK_EXCEPTION
                          createTime:
                            type: string
                            description: Creation time
                            format: date-time
                          errorCode:
                            type: number
                            description: >-
                              Error code, valid when task fails


                              - **200**: Success - Request has been processed
                              successfully

                              - **500**: Internal Error - Please try again
                              later.
                            enum:
                              - 200
                              - 500
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
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
                    audioWavUrl: https://example.com/s/04e6****e727.wav
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
      x-apidog-folder: docs/en/Market/Suno API/WAV Conversion
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506299-run
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
