# Get 4o Image Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/gpt4o-image/record-info:
    get:
      summary: Get 4o Image Details
      deprecated: false
      description: >-
        Query 4o Image generation task details using taskId, including
        generation status, parameters and results.


        ### Status Descriptions

        - GENERATING: Generating in progress

        - SUCCESS: Generation successful

        - CREATE_TASK_FAILED: Failed to create task

        - GENERATE_FAILED: Generation failed


        ### Important Notes

        - Maximum query rate is 3 times per second per task
      operationId: get-4o-image-details
      tags:
        - docs/en/Market/Image    Models/4o Image API
      parameters:
        - name: taskId
          in: query
          description: Unique identifier of the 4o image generation task
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
                          - 402
                          - 404
                          - 422
                          - 429
                          - 455
                          - 500
                        description: >-
                          Response Status Codes


                          - **200**: Success - Request has been processed
                          successfully  

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid  

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation  

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
                            - Build Failed - vocal removal generation failed
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
                            description: Unique identifier of the 4o image generation task
                            examples:
                              - task12345
                          paramJson:
                            type: string
                            description: Request parameters
                            examples:
                              - >-
                                {"prompt":"A beautiful sunset over the
                                mountains","size":"1:1","isEnhance":false}
                          completeTime:
                            type: integer
                            format: int64
                            description: Task completion time
                            examples:
                              - 1672574400000
                          response:
                            type: object
                            description: Final result
                            properties:
                              resultUrls:
                                type: array
                                items:
                                  type: string
                                description: List of generated image URLs
                                examples:
                                  - - https://example.com/result/image1.png
                            x-apidog-orders:
                              - resultUrls
                            x-apidog-ignore-properties: []
                          successFlag:
                            type: integer
                            format: int32
                            description: Generation status flag
                            examples:
                              - 1
                          status:
                            type: string
                            description: >-
                              Generation status text, possible values:
                              GENERATING-In progress, SUCCESS-Successful,
                              CREATE_TASK_FAILED-Task creation failed,
                              GENERATE_FAILED-Generation failed


                              - **200**: Success - Image generation completed
                              successfully  

                              - **400**: Bad Request  
                                - The image content in filesUrl violates content policy  
                                - Image size exceeds maximum of 26214400 bytes  
                                - We couldn't process the provided image file (code=invalid_image_format)  
                                - Your content was flagged by OpenAI as violating content policies  
                                - Failed to fetch the image. Kindly verify any access limits set by you or your service provider  
                              - **451**: Download Failed - Unable to download
                              image from the provided filesUrl  

                              - **500**: Internal Error  
                                - Failed to get user token  
                                - Please try again later  
                                - Failed to generate image  
                                - GPT 4O failed to edit the picture  
                                - null
                            enum:
                              - GENERATING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_FAILED
                            examples:
                              - SUCCESS
                          errorCode:
                            type: integer
                            format: int32
                            description: Error code
                            enum:
                              - 200
                              - 400
                              - 451
                              - 500
                          errorMessage:
                            type: string
                            description: Error message
                            examples:
                              - ''
                          createTime:
                            type: integer
                            format: int64
                            description: Creation time
                            examples:
                              - 1672561200000
                          progress:
                            type: string
                            description: >-
                              Progress, minimum value is "0.00", maximum value
                              is "1.00"
                            examples:
                              - '1.00'
                        x-apidog-orders:
                          - taskId
                          - paramJson
                          - completeTime
                          - response
                          - successFlag
                          - status
                          - errorCode
                          - errorMessage
                          - createTime
                          - progress
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
                    {"prompt":"A beautiful sunset over the
                    mountains","size":"1:1","isEnhance":false}
                  completeTime: 1672574400000
                  response:
                    resultUrls:
                      - https://example.com/result/image1.png
                  successFlag: 1
                  status: SUCCESS
                  errorCode: null
                  errorMessage: ''
                  createTime: 1672561200000
                  progress: '1.00'
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
      x-apidog-folder: docs/en/Market/Image    Models/4o Image API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506279-run
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
