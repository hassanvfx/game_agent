# 获取生成文件的下载链接

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/common/download-url:
    post:
      summary: 获取生成文件的下载链接
      deprecated: false
      description: |
        :::tip[]
          将生成的文件URL转换为可下载的临时链接。仅支持kie.ai服务生成的文件。
        :::

        ### 功能特性

        * 将kie.ai生成的文件URL转换为可下载链接
        * 支持kie.ai平台生成的所有文件类型（图片、视频、音频等）
        * 临时下载链接有效期为20分钟
        * 安全访问生成的内容
        * API Key身份验证保护

        ### 重要说明

        :::warning[]
        仅支持kie.ai服务生成的文件URL。外部文件URL将返回422验证错误。
        :::

        :::tip[]
        可下载链接20分钟后过期。请确保在此时间范围内下载或缓存内容。
        :::
      operationId: download-url
      tags:
        - docs/zh-CN/Common API
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                url:
                  type: string
                  format: uri
                  description: kie.ai服务生成的文件URL。不支持外部文件URL。
                  examples:
                    - https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98
              required:
                - url
              x-apidog-orders:
                - url
              x-apidog-ignore-properties: []
            examples: {}
      responses:
        '200':
          description: 请求成功
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
                          - 505
                        description: |-
                          响应状态码

                          | Code | 说明 |
                          |------|------|
                          | 200 | 成功 - 请求已成功处理 |
                          | 401 | 未授权 - 缺少身份验证凭据或凭据无效 |
                          | 402 | 积分不足 - 账户没有足够的积分执行此操作 |
                          | 404 | 未找到 - 请求的资源或接口不存在 |
                          | 422 | 参数错误 - URL无效（不支持外部文件URL） |
                          | 429 | 超出限制 - 已超过该资源的请求限制 |
                          | 455 | 服务不可用 - 系统维护中 |
                          | 500 | 服务器错误 - 处理请求时发生意外错误 |
                          | 505 | 功能已禁用 - 当前功能不可用 |
                      msg:
                        type: string
                        description: 当 code != 200 时的错误信息
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
                        format: uri
                        description: 文件的可下载链接。有效期为20分钟。
                        examples:
                          - >-
                            https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data: https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98
          headers: {}
          x-apidog-name: ''
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
      x-apidog-folder: docs/zh-CN/Common API
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506755-run
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
