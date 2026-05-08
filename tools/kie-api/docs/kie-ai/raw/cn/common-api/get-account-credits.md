# 获取剩余积分

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/chat/credit:
    get:
      summary: 获取剩余积分
      deprecated: false
      description: |-

        :::tip[]
          获取您账户中可用的当前积分余额。
        :::

        ### 使用指南

        * 使用此接口检查您当前的积分余额
        * 监控使用情况以确保有足够的积分继续使用服务
        * 根据使用模式计划积分补充

        ### 开发者注意事项

        * 所有生成服务都需要积分余额
        * 积分耗尽时服务访问将受到限制
        * 积分消耗基于特定服务和使用量
      operationId: get-account-credits
      tags:
        - docs/zh-CN/Common API
      parameters: []
      responses:
        '200':
          description: 请求成功
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
                      | 422 | 参数错误 - 请求参数未通过校验 |
                      | 429 | 超出限制 - 已超过该资源的请求限制 |
                      | 455 | 服务不可用 - 系统维护中 |
                      | 500 | 服务器错误 - 处理请求时发生意外错误 |
                      | 505 | 功能已禁用 - 当前功能不可用 |
                  msg:
                    type: string
                    description: 当 code != 200 时的错误信息
                    examples:
                      - success
                  data:
                    type: integer
                    description: 剩余积分数量
                    examples:
                      - 100
                required:
                  - code
                  - msg
                  - data
                x-apidog-orders:
                  - code
                  - msg
                  - data
                x-apidog-ignore-properties: []
              example:
                code: 200
                msg: success
                data: 100
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506754-run
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
