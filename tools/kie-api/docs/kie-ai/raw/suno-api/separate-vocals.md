# Vocal & Instrument Stem Separation

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/vocal-removal/generate:
    post:
      summary: Vocal & Instrument Stem Separation
      deprecated: false
      description: "Separate music into vocal, instrumental, and individual instrument tracks using advanced audio processing technology.\n\n### Usage Guide\n\n- Separate a platform‑generated mix into vocal, instrumental, and individual instrument components.\n- Two processing modes are available:\n  - `separate_vocal` — 2‑stem split\n  - `split_stem`   — up to 12‑stem split\n- Ideal for karaoke creation, remixes, sample extraction, or detailed post‑production.\n- Best results on professionally mixed AI tracks with clear vocal and instrumental layers.\n- **Billing notice:** Each call consumes credits; **re‑calling the same track is charged again** (no server‑side caching).\n- **Pricing:** Check current per‑call credit costs at [**https://kie.ai/pricing**](https://kie.ai/pricing).\n\n### Separation Mode Details\n\n| **Mode (<code>type</code>)** | **Stems Returned** | **Typical Use** | **Credit Cost** |\n| :--------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------ | :----------------------------- |\n| `separate_vocal` _(default)_ | **2 stems** – Vocals \\+ Instrumental                                                                                               | Quick vocal removal, karaoke, basic remixes | **10 Credits**  |\n| `split_stem`                 | **Up to 12 stems** – Vocals, Backing Vocals, Drums, Bass, Guitar, Keyboard, Strings, Brass, Woodwinds, Percussion, Synth, FX/Other | Advanced mixing, remixing, sound design     | **50 Credits** |\n\n### Parameter\_Reference\n\n| Name      | Type   | Description                                                     |\n| :-------- | :----- | :-------------------------------------------------------------- |\n| `taskId`  | string | ID of the original music‑generation task                        |\n| `audioId` | string | Which audio variation to process when multiple versions exist   |\n| `type`    | string | **Required.** Separation mode: `separate_vocal` or `split_stem` |\n\n### Developer Notes\n\n- All returned audio‑file URLs remain accessible for **14 days**.\n- Separation quality depends on the complexity and mixing of the original track.\n- `separate_vocal` returns **2 stems** — vocals \\+ instrumental.\n- `split_stem` returns **up to 12 independent stems** — vocals, backing vocals, drums, bass, guitar, keyboard, strings, brass, woodwinds, percussion, synth, FX/other.\n- **Billing:** Every request is charged. Re‑submitting the same track triggers **a new credit deduction** (no server‑side caching)."
      operationId: separate-vocals
      tags:
        - docs/en/Market/Suno API/Vocal Removal
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - taskId
                - audioId
                - callBackUrl
              properties:
                taskId:
                  type: string
                  description: >-
                    Unique identifier of the music generation task. This should
                    be a taskId returned from either the "Generate Music" or
                    "Extend Music" endpoints.
                  examples:
                    - 5c79****be8e
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the specific audio track to process for
                    vocal separation. This ID is returned in the callback data
                    after music generation completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                type:
                  type: string
                  enum:
                    - separate_vocal
                    - split_stem
                  default: separate_vocal
                  description: >-
                    Separation type with the following options:


                    - **separate_vocal**: Separate vocals and accompaniment,
                    generating vocal and instrumental tracks

                    - **split_stem**: Separate various instrument sounds,
                    generating vocals, backing vocals, drums, bass, guitar,
                    keyboard, strings, brass, woodwinds, percussion,
                    synthesizer, effects, and other tracks
                  examples:
                    - separate_vocal
                callBackUrl:
                  type: string
                  format: uri
                  description: >-
                    The URL to receive vocal separation task completion updates.
                    Required for all vocal separation requests.


                    - System will POST task status and results to this URL when
                    vocal separation completes

                    - Callback content varies based on the type parameter:
                    separate_vocal returns vocals and accompaniment, split_stem
                    returns multiple instrument tracks

                    - Your callback endpoint should accept POST requests with
                    JSON payload containing separated audio file links

                    - For detailed callback format and implementation guide, see
                    [Vocal Separation
                    Callbacks](https://docs.kie.ai/suno-api/separate-vocals-callbacks)

                    - Alternatively, use the Get Vocal Separation Details
                    endpoint to poll task status

                    - To ensure callback security, see [Webhook Verification
                    Guide](/common-api/webhook-verification) for signature
                    verification implementation
                  examples:
                    - https://api.example.com/callback
              x-apidog-orders:
                - taskId
                - audioId
                - type
                - callBackUrl
              x-apidog-ignore-properties: []
            example:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
              callBackUrl: https://api.example.com/callback
              type: separate_vocal
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
                          - 402
                          - 404
                          - 409
                          - 422
                          - 429
                          - 455
                          - 500
                        description: >-
                          Response status code


                          - **200**: Success - Request has been processed
                          successfully

                          - **400**: Format Error - The parameter is not in a
                          valid JSON format

                          - **401**: Unauthorized - Authentication credentials
                          are missing or invalid

                          - **402**: Insufficient Credits - Account does not
                          have enough credits to perform the operation

                          - **404**: Not Found - The requested resource or
                          endpoint does not exist

                          - **409**: Conflict - WAV record already exists

                          - **422**: Validation Error - The request parameters
                          failed validation checks

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource

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
                            description: Task ID for tracking task status
                            examples:
                              - 5c79****be8e
                        x-apidog-orders:
                          - taskId
                        x-apidog-ignore-properties: []
                    x-apidog-orders:
                      - data
                    x-apidog-ignore-properties: []
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
        vocalRemovalGenerated:
          '{$request.body#/callBackUrl}':
            post:
              description: >-
                System will call this callback when vocal separation is
                complete. Callback data structure varies based on the type
                parameter specified in the request.


                ### separate_vocal Type Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "vocal separation generated successfully.",
                  "data": {
                    "task_id": "3e63b4cc88d52611159371f6af5571e7",
                    "vocal_separation_info": {
                      "instrumental_url": "https://file.aiquickdraw.com/s/d92a13bf-c6f4-4ade-bb47-f69738435528_Instrumental.mp3",
                      "origin_url": "",
                      "vocal_url": "https://file.aiquickdraw.com/s/3d7021c9-fa8b-4eda-91d1-3b9297ddb172_Vocals.mp3"
                    }
                  }
                }

                ```


                ### split_stem Type Callback Example

                ```json

                {
                  "code": 200,
                  "msg": "vocal separation generated successfully.",
                  "data": {
                    "task_id": "e649edb7abfd759285bd41a47a634b10",
                    "vocal_separation_info": {
                      "origin_url": "",
                      "backing_vocals_url": "https://file.aiquickdraw.com/s/aadc51a3-4c88-4c8e-a4c8-e867c539673d_Backing_Vocals.mp3",
                      "bass_url": "https://file.aiquickdraw.com/s/a3c2da5a-b364-4422-adb5-2692b9c26d33_Bass.mp3",
                      "brass_url": "https://file.aiquickdraw.com/s/334b2d23-0c65-4a04-92c7-22f828afdd44_Brass.mp3",
                      "drums_url": "https://file.aiquickdraw.com/s/ac75c5ea-ac77-4ad2-b7d9-66e140b78e44_Drums.mp3",
                      "fx_url": "https://file.aiquickdraw.com/s/a8822c73-6629-4089-8f2a-d19f41f0007d_FX.mp3",
                      "guitar_url": "https://file.aiquickdraw.com/s/064dd08e-d5d2-4201-9058-c5c40fb695b4_Guitar.mp3",
                      "keyboard_url": "https://file.aiquickdraw.com/s/adc934e0-df7d-45da-8220-1dba160d74e0_Keyboard.mp3",
                      "percussion_url": "https://file.aiquickdraw.com/s/0f70884d-047c-41f1-a6d0-7044618b7dc6_Percussion.mp3",
                      "strings_url": "https://file.aiquickdraw.com/s/49829425-a5b0-424e-857a-75d4c63a426b_Strings.mp3",
                      "synth_url": "https://file.aiquickdraw.com/s/56b2d94a-eb92-4d21-bc43-3460de0c8348_Synth.mp3",
                      "vocal_url": "https://file.aiquickdraw.com/s/07420749-29a2-4054-9b62-e6a6f8b90ccb_Vocals.mp3",
                      "woodwinds_url": "https://file.aiquickdraw.com/s/d81545b1-6f94-4388-9785-1aaa6ecabb02_Woodwinds.mp3"
                    }
                  }
                }

                ```
              requestBody:
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


                                - **200**: Success - Request has been processed
                                successfully

                                - **500**: Internal Error - Please try again
                                later.
                            msg:
                              type: string
                              description: Error message when code != 200
                              example: success
                        - type: object
                          properties:
                            data:
                              type: object
                              properties:
                                taskId:
                                  type: string
                                  description: Task ID for tracking task status
                                  example: 5c79****be8e
                      type: object
                      properties:
                        code:
                          type: integer
                          description: Status code
                          example: 200
                        msg:
                          type: string
                          description: Response message
                          example: vocal separation generated successfully.
                        data:
                          type: object
                          properties:
                            task_id:
                              type: string
                              description: Task ID
                            vocal_separation_info:
                              type: object
                              description: >-
                                Vocal separation result information, fields vary
                                based on the type parameter in the request
                              properties:
                                origin_url:
                                  type: string
                                  description: Original audio URL
                                vocal_url:
                                  type: string
                                  description: Vocal part audio URL
                                instrumental_url:
                                  type: string
                                  description: >-
                                    Instrumental part audio URL (separate_vocal
                                    type only)
                                backing_vocals_url:
                                  type: string
                                  description: >-
                                    Backing vocals audio URL (split_stem type
                                    only)
                                drums_url:
                                  type: string
                                  description: Drums part audio URL (split_stem type only)
                                bass_url:
                                  type: string
                                  description: Bass part audio URL (split_stem type only)
                                guitar_url:
                                  type: string
                                  description: Guitar part audio URL (split_stem type only)
                                keyboard_url:
                                  type: string
                                  description: >-
                                    Keyboard part audio URL (split_stem type
                                    only)
                                percussion_url:
                                  type: string
                                  description: >-
                                    Percussion part audio URL (split_stem type
                                    only)
                                strings_url:
                                  type: string
                                  description: >-
                                    Strings part audio URL (split_stem type
                                    only)
                                synth_url:
                                  type: string
                                  description: >-
                                    Synthesizer part audio URL (split_stem type
                                    only)
                                fx_url:
                                  type: string
                                  description: >-
                                    Effects part audio URL (split_stem type
                                    only)
                                brass_url:
                                  type: string
                                  description: Brass part audio URL (split_stem type only)
                                woodwinds_url:
                                  type: string
                                  description: >-
                                    Woodwinds part audio URL (split_stem type
                                    only)
              responses:
                '200':
                  description: Callback received successfully
      x-apidog-folder: docs/en/Market/Suno API/Vocal Removal
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506300-run
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
