# Generate Persona

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/generate/generate-persona:
    post:
      summary: Generate Persona
      deprecated: false
      description: >-

        > Create a personalized music Persona based on generated music, giving
        the music a unique identity and characteristics.


        ## Usage Guide


        Use this endpoint to create Personas (music characters) for generated
        music:

        * Requires the `taskId` from music generation related endpoints
        (generate, extend, cover, upload-extend) and audio ID

        * Customize the Persona name and description to give music unique
        personality

        * Generated Personas can be used for subsequent music creation and style
        transfer


        ## Parameter Details


        *   **`taskId`** (Required): Can be obtained from the following
        endpoints:
            *   [Generate Music](/suno-api/generate-music) (`/api/v1/generate`)
            *   [Extend Music](/suno-api/extend-music) (`/api/v1/generate/extend`)
            *   [Upload And Cover Audio](/suno-api/upload-and-cover-audio) (`/api/v1/generate/upload-cover`)
            *   [Upload And Extend Audio](/suno-api/upload-and-extend-audio) (`/api/v1/generate/upload-extend`)
        *   **`audioId`** (Required): Specifies the audio ID to create Persona
        for

        *   **`name`** (Required): Assigns an easily recognizable name to the
        Persona

        *   **`description`** (Required): Describes the Persona's musical
        characteristics, style, and personality


        ## Developer Notes


        :::caution Important Requirements

        *   **Ensure the music generation task is fully completed** before
        calling this endpoint. If the music is still generating, this endpoint
        will return a failure.

        *   **Model Requirement**: Persona generation only supports `taskId`
        from music generated with models above v3.5 (v3.5 itself is **not**
        supported).

        *   Each audio ID can only generate a Persona **once**.

        :::


        *   It is recommended to provide detailed descriptions for Personas to
        better capture musical characteristics.

        *   The returned `personaId` can be used in subsequent music generation
        requests to create music with similar style characteristics.

        *   You can apply the `personaId` to the following endpoints:
            *   [Generate Music](/suno-api/generate-music)
            *   [Extend Music](/suno-api/extend-music)
            *   [Upload And Cover Audio](/suno-api/upload-and-cover-audio)
            *   [Upload And Extend Audio](/suno-api/upload-and-extend-audio)

        ## Parameter Example


        ```json

        {
          "taskId": "5c79****be8e",
          "audioId": "e231****-****-****-****-****8cadc7dc",
          "name": "Electronic Pop Singer",
          "description": "A modern electronic music style pop singer, skilled in dynamic rhythms and synthesizer tones"
        }

        ```


        :::note

        Ensure that the music generation task corresponding to the `taskId` is
        complete and the `audioId` is within the valid range.

        :::


        :::tip

        Providing detailed and specific descriptions for Personas helps the
        system more accurately capture musical style characteristics.

        :::
      operationId: generate-persona
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
                - audioId
                - name
                - description
              properties:
                taskId:
                  type: string
                  description: >-
                    Unique identifier of the original music generation task.
                    This can be a taskId returned from any of the following
                    endpoints:

                    - Generate Music (/api/v1/generate)

                    - Extend Music (/api/v1/generate/extend)

                    - Upload And Cover Audio (/api/v1/generate/upload-cover)

                    - Upload And Extend Audio (/api/v1/generate/upload-extend)
                  examples:
                    - 5c79****be8e
                audioId:
                  type: string
                  description: >-
                    Unique identifier of the audio track to create Persona for.
                    This ID is returned in the callback data after music
                    generation completes.
                  examples:
                    - e231****-****-****-****-****8cadc7dc
                name:
                  type: string
                  description: >-
                    Name for the Persona. A descriptive name that captures the
                    essence of the musical style or character.
                  examples:
                    - Electronic Pop Singer
                description:
                  type: string
                  description: >-
                    Detailed description of the Persona's musical
                    characteristics, style, and personality. Be specific about
                    genre, mood, instrumentation, and vocal qualities.
                  examples:
                    - >-
                      A modern electronic music style pop singer, skilled in
                      dynamic rhythms and synthesizer tones
                ' vocalStart':
                  type: number
                  description: >-
                    Start time (in seconds) for Persona analysis segment
                    extraction. Used to specify the time point in the audio from
                    which to extract the segment for Persona analysis. Must be
                    less than vocalEnd, and vocalEnd - vocalStart must be
                    between 10–30 seconds. Defaults to 0.0.
                  default: 0
                  examples:
                    - 12.5
                  minimum: 0
                ' vocalEnd':
                  type: number
                  description: >-
                    End time (in seconds) for Persona analysis segment
                    extraction. Together with vocalStart, used to specify the
                    time range for analysis. vocalEnd - vocalStart must be
                    between 10–30 seconds. Defaults to 30.0.
                  multipleOf: 0.01
                  default: 30
                  examples:
                    - 25.8
                  minimum: 0
                style:
                  type: string
                  description: >-
                    Optional. Used to supplement the description of the music
                    style tag corresponding to the Persona, such as "Electronic
                    Pop", "Jazz Trio", etc.
              x-apidog-orders:
                - taskId
                - audioId
                - name
                - description
                - ' vocalStart'
                - ' vocalEnd'
                - style
              x-apidog-ignore-properties: []
            example:
              taskId: 5c79****be8e
              audioId: e231****-****-****-****-****8cadc7dc
              name: Electronic Pop Singer
              description: >-
                A modern electronic music style pop singer, skilled in dynamic
                rhythms and synthesizer tones
              vocalStart: 0
              vocalEnd: 30
              style: Electronic Pop
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
                          - 409
                          - 422
                          - 429
                          - 451
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

                          - **409**: Conflict - Persona already exists for this
                          music

                          - **422**: Validation Error - The request parameters
                          failed validation checks  

                          - **429**: Rate Limited - Request limit has been
                          exceeded for this resource  

                          - **451**: Unauthorized - Failed to fetch the music
                          data. Kindly verify any access limits set by you or
                          your service provider  

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
                          personaId:
                            type: string
                            description: >-
                              Unique identifier for the generated Persona. This
                              personaId can be used in subsequent music
                              generation requests (Generate Music, Extend Music,
                              Upload And Cover Audio, Upload And Extend Audio)
                              to create music with similar style
                              characteristics.
                            examples:
                              - a1b2****c3d4
                          name:
                            type: string
                            description: Name of the Persona as provided in the request.
                            examples:
                              - Electronic Pop Singer
                          description:
                            type: string
                            description: >-
                              Description of the Persona's musical
                              characteristics, style, and personality as
                              provided in the request.
                            examples:
                              - >-
                                A modern electronic music style pop singer,
                                skilled in dynamic rhythms and synthesizer tones
                        x-apidog-orders:
                          - personaId
                          - name
                          - description
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
      x-apidog-folder: docs/en/Market/Suno API/Music Generation
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506295-run
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
