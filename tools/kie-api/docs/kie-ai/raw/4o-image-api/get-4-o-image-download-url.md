# Get Direct Download URL

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/gpt4o-image/download-url:
    post:
      summary: Get Direct Download URL
      deprecated: false
      description: >-
        Convert an image URL to a direct download URL. This helps solve
        cross-domain issues when downloading images directly. The returned URL
        is valid for 20 minutes.
      operationId: get-4o-image-download-url
      tags:
        - docs/en/Market/Image    Models/4o Image API
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                taskId:
                  type: string
                  description: The task ID associated with the image generation
                  examples:
                    - task12345
                url:
                  type: string
                  format: uri
                  description: >-
                    The original image URL that needs to be converted to a
                    direct download URL
                  examples:
                    - https://tempfile.aiquickdraw.com/v/xxxxxxx.png
              required:
                - taskId
                - url
              x-apidog-orders:
                - taskId
                - url
              examples:
                - taskId: task12345
                  url: https://tempfile.aiquickdraw.com/v/xxxxxxx.png
              x-apidog-ignore-properties: []
            example:
              taskId: task12345
              url: https://tempfile.aiquickdraw.com/v/xxxxxxx.png
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
                          Response Status Codes


                          - **200**: Success - Request has been processed
                          successfully  

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid  

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist  

                          - **422**: Validation Error  
                            - The request parameters failed validation checks  
                            - record is null  
                            - Temporarily supports records within 14 days  
                            - record result data is blank  
                            - record status is not success  
                            - record result data not exist  
                            - record result data is empty  
                          - **451**: Failed to fetch the image. Kindly verify
                          any access limits set by you or your service
                          provider  

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
                        type: string
                        description: Direct download URL valid for 20 minutes
                        examples:
                          - >-
                            https://xxxxxx.xxxxxxxx.r2.cloudflarestorage.com/v/xxxxxxx.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250415T101007Z&X-Amz-SignedHeaders=host&X-Amz-Expires=1200&X-Amz-Credential=2464206aa3e576aa7c035d889be3a84e%2F20250415%2Fapac%2Fs3%2Faws4_request&X-Amz-Signature=122ae8bef09110e620841ab2ef8061c1818e754fc201408a9d1c6847b36fd3df
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data: >-
                  https://xxxxxx.xxxxxxxx.r2.cloudflarestorage.com/v/xxxxxxx.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250415T101007Z&X-Amz-SignedHeaders=host&X-Amz-Expires=1200&X-Amz-Credential=2464206aa3e576aa7c035d889be3a84e%2F20250415%2Fapac%2Fs3%2Faws4_request&X-Amz-Signature=122ae8bef09110e620841ab2ef8061c1818e754fc201408a9d1c6847b36fd3df
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506280-run
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
