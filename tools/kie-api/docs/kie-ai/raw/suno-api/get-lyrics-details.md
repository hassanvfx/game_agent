# Get Lyrics Task Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/lyrics/record-info:
    get:
      summary: Get Lyrics Task Details
      deprecated: false
      description: >-
        Retrieve detailed information about a lyrics generation task.


        ### Usage Guide

        - Use this endpoint to check the status of a lyrics generation task

        - Retrieve generated lyrics content once the task is complete

        - Track task progress and access any error information if generation
        failed


        ### Status Descriptions

        - `PENDING`: Task is waiting to be processed

        - `SUCCESS`: Lyrics generated successfully

        - `CREATE_TASK_FAILED`: Failed to create the task

        - `GENERATE_LYRICS_FAILED`: Failed during lyrics generation

        - `CALLBACK_EXCEPTION`: Error occurred during callback

        - `SENSITIVE_WORD_ERROR`: Content filtered due to sensitive words


        ### Developer Notes

        - Successful tasks will include multiple lyrics variations

        - Each lyrics set includes both content and a suggested title

        - Error codes and messages are provided for failed tasks
      operationId: get-lyrics-details
      tags:
        - docs/en/Market/Suno API/Lyrics Generation
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the lyrics generation task to retrieve. This is
            the taskId returned when creating the lyrics generation task.
          required: true
          example: 11dc****8b0f
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
                          - 400
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

                          - **400**: Please try rephrasing   with more specific
                          details or using a different approach.

                          Song Description contained artist name:

                          Song Description flagged for moderation

                          Unable to generate lyrics from song   description

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

                          Internal Error - Please try again later.
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
                          param:
                            type: string
                            description: Parameter information for task generation
                          response:
                            type: object
                            properties:
                              taskId:
                                type: string
                                description: Task ID
                              data:
                                type: array
                                items:
                                  type: object
                                  properties:
                                    text:
                                      type: string
                                      description: Lyrics content
                                    title:
                                      type: string
                                      description: Lyrics title
                                    status:
                                      type: string
                                      description: Generation status
                                      enum:
                                        - complete
                                        - failed
                                    errorMessage:
                                      type: string
                                      description: >-
                                        Error message, valid when status is
                                        failed
                                  x-apidog-orders:
                                    - text
                                    - title
                                    - status
                                    - errorMessage
                                  x-apidog-ignore-properties: []
                            x-apidog-orders:
                              - taskId
                              - data
                            x-apidog-ignore-properties: []
                          status:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_LYRICS_FAILED
                              - CALLBACK_EXCEPTION
                              - SENSITIVE_WORD_ERROR
                          type:
                            type: string
                            description: Task type
                            examples:
                              - LYRICS
                          errorCode:
                            type: number
                            description: >-
                              Error code, valid when task fails


                              - **200**: Success - Request has been processed
                              successfully

                              - **400**: Please try rephrasing   with more
                              specific details or using a different approach.

                              Song Description contained artist name

                              Song Description flagged for moderation

                              Unable to generate lyrics from song   description

                              - **500**: Internal Error - Please try again
                              later.
                            enum:
                              - 200
                              - 400
                              - 500
                          errorMessage:
                            type: string
                            description: Error message, valid when task fails
                        x-apidog-orders:
                          - taskId
                          - param
                          - response
                          - status
                          - type
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
                  taskId: 11dc****8b0f
                  param: '{"prompt":"A song about peaceful night in the city"}'
                  response:
                    taskId: 11dc****8b0f
                    data:
                      - text: |-
                          [Verse]
                          我穿越城市黑暗夜
                          心中燃烧梦想的烈火
                        title: 钢铁侠
                        status: complete
                        errorMessage: ''
                  status: SUCCESS
                  type: LYRICS
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
      x-apidog-folder: docs/en/Market/Suno API/Lyrics Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506297-run
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
