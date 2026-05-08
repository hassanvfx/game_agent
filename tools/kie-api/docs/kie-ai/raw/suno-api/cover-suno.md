# Generate Music Cover

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/suno/cover/generate:
    post:
      summary: Generate Music Cover
      deprecated: false
      description: >-
        Generate personalized cover images based on original music tasks.


        ### Usage Guide

        - Use this interface to create personalized cover images for generated
        music

        - Requires the taskId of the original music task

        - Each music task can only generate a Cover once; duplicate requests
        will return the existing taskId

        - Results will be notified through the callback URL upon completion


        ### Parameter Details

        - `taskId` identifies the unique identifier of the original music
        generation task

        - `callBackUrl` receives callback address for completion notifications


        ### Developer Notes

        - Cover image file URLs will be retained for 14 days

        - If a Cover has already been generated for this music task, a 400
        status code and existing taskId will be returned

        - It's recommended to call this interface after music generation is
        complete

        - Usually generates 2 different style images for selection
      operationId: generate-cover
      tags:
        - docs/en/Market/Suno API/Music Generation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
              properties:
                taskId:
                  type: string
                  description: >-
                    Original music task ID, should be the taskId returned by the
                    music generation interface.
                  examples:
                    - 73d6128b3523a0079df10da9471017c8
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    URL address for receiving Cover generation task completion
                    updates. This parameter is required for all Cover generation
                    requests.


                    - The system will send POST requests to this URL when Cover
                    generation is complete, including task status and results

                    - Your callback endpoint should be able to accept JSON
                    payloads containing cover image URLs

                    - For detailed callback format and implementation guide, see
                    [Cover Generation
                    Callbacks](https://docs.kie.ai/suno-api/cover-suno-callbacks)

                    - Alternatively, you can use the Get Cover Details interface
                    to poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
              x-apidog-orders:
                - taskId
                - callBackUrl
              x-apidog-ignore-properties: []
            example:
              taskId: 73d6128b3523a0079df10da9471017c8
              callBackUrl: https://api.example.com/callback
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

                          - **400**: Validation error - Cover already generated
                          for this task

                          - **401**: Unauthorized - Authentication credentials
                          missing or invalid

                          - **402**: Insufficient credits - Account doesn't have
                          enough credits for this operation

                          - **404**: Not found - Requested resource or endpoint
                          doesn't exist

                          - **409**: Conflict - Cover record already exists

                          - **422**: Validation error - Request parameters
                          failed validation checks

                          - **429**: Rate limited - Your call frequency is too
                          high. Please try again later.

                          - **455**: Service unavailable - System currently
                          undergoing maintenance

                          - **500**: Server error - Unexpected error occurred
                          while processing request

                          Build failed - Cover image generation failed
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
                    x-apidog-orders:
                      - taskId
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
        onCoverGenerated:
          '{$request.body#/callBackUrl}':
            post:
              summary: Cover generation completion callback
              description: >-
                When Cover generation is complete, the system will send a POST
                request to the provided callback URL to notify results
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


                                - **200**: Success - Request processed
                                successfully

                                - **500**: Internal error - Please try again
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
                          description: Status code, 200 indicates success
                          example: 200
                        msg:
                          type: string
                          description: Status message
                          example: success
                        data:
                          type: object
                          required:
                            - taskId
                            - images
                          properties:
                            taskId:
                              type: string
                              description: Unique identifier of the generation task
                              example: 21aee3c3c2a01fa5e030b3799fa4dd56
                            images:
                              type: array
                              items:
                                type: string
                              description: >-
                                Array of accessible cover image URLs, valid for
                                14 days
                              example:
                                - >-
                                  https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png
                                - >-
                                  https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506292-run
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
