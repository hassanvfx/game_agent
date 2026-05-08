# Get 1080P Video

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/veo/get-1080p-video:
    get:
      summary: Get 1080P Video
      deprecated: false
      description: >
        ::: info[]
          Get the high-definition 1080P version of a Veo 3.1 video generation task.
        :::


        ::: note[]
          Legacy note: If your task was generated via a deprecated fallback path, 1080P may already be the default output and this endpoint may not apply.
        :::


        ### Usage Instructions


        * 1080P generation requires extra processing time — typically **~1–3
        minutes** depending on load.

        * If the 1080P video is not ready yet, the endpoint may return a non-200
        code. In this case, wait a bit and retry (recommended interval:
        **20–30s**) until the result is available.

        * Make sure the **original generation task is successful** before
        requesting 1080P.
      operationId: get-veo3-1-1080p-video
      tags:
        - docs/en/Market/Veo3.1 API
      parameters:
        - name: taskId
          in: query
          description: Task ID
          required: true
          example: veo_task_abcdef123456
          schema:
            type: string
        - name: index
          in: query
          description: video index
          required: false
          example: 0
          schema:
            type: integer
      responses:
        '200':
          description: Request successful
          content:
            application/json:
              schema:
                type: object
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

                      - **401**: Unauthorized - Authentication credentials are
                      missing or invalid

                      - **404**: Not Found - The requested resource or endpoint
                      does not exist

                      - **422**: Validation Error - The request parameters
                      failed validation checks.

                      record is null.

                      Temporarily supports records within 14 days.

                      record result data is blank.

                      record status is not success.

                      record result data not exist.

                      record result data is empty.

                      - **429**: Rate Limited - Request limit has been exceeded
                      for this resource

                      - **451**: Failed to fetch the image. Kindly verify any
                      access limits set by you or your service provider.

                      - **455**: Service Unavailable - System is currently
                      undergoing maintenance

                      - **500**: Server Error - An unexpected error occurred
                      while processing the request
                  msg:
                    type: string
                    description: Error message when code != 200
                    examples:
                      - success
                  data:
                    type: object
                    properties:
                      resultUrl:
                        type: string
                        description: 1080P high-definition video download URL
                        examples:
                          - >-
                            https://tempfile.aiquickdraw.com/p/42f4f8facbb040c0ade87c27cb2d5e58_1749711595.mp4
                    x-apidog-orders:
                      - resultUrl
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
                  resultUrl: >-
                    https://tempfile.aiquickdraw.com/p/42f4f8facbb040c0ade87c27cb2d5e58_1749711595.mp4
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
      x-apidog-folder: docs/en/Market/Veo3.1 API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506313-run
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
