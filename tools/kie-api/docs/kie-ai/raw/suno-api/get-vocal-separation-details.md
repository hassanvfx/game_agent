# Get Vocal Separation Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/vocal-removal/record-info:
    get:
      summary: Get Vocal Separation Details
      deprecated: false
      description: >-
        Retrieve detailed information about a vocal separation task.


        ### Usage Guide

        - Use this endpoint to check the status of a vocal separation task

        - Access the URLs for vocal, instrumental, and individual instrument
        tracks once processing is complete

        - Track processing progress and any errors that may have occurred

        - Supports querying results for both `separate_vocal` and `split_stem`
        separation types


        ### Status Descriptions

        - `PENDING`: Task is waiting to be processed

        - `SUCCESS`: Vocal separation completed successfully

        - `CREATE_TASK_FAILED`: Failed to create the separation task

        - `GENERATE_AUDIO_FAILED`: Failed during audio processing

        - `CALLBACK_EXCEPTION`: Error occurred during callback


        ### Response Data Structure Description

        - `separate_vocal` type: Returns `instrumentalUrl` and `vocalUrl`
        fields, other instrument fields are null

        - `split_stem` type: Returns detailed instrument separation fields,
        `instrumentalUrl` is null


        ### Developer Notes

        - Separated audio file URLs are only available when status is `SUCCESS`

        - Error codes and messages are provided for failed tasks

        - Separated audio files are retained for 14 days after successful
        processing

        - Field structure varies based on the `type` parameter from the original
        request
      operationId: get-vocal-separation-details
      tags:
        - docs/en/Market/Suno API/Vocal Removal
      parameters:
        - name: taskId
          in: query
          description: >-
            Unique identifier of the vocal separation task to retrieve. This is
            the taskId returned when creating the vocal separation task.
          required: true
          example: 5e72****97c7
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
                            description: >-
                              Vocal separation response result, fields vary
                              based on the type parameter from the original
                              request
                            properties:
                              id:
                                type: string
                                description: Response ID
                                nullable: true
                              originUrl:
                                type: string
                                description: Original audio URL
                              originData:
                                type: array
                                description: Array of separated audio track information
                                items:
                                  type: object
                                  properties:
                                    duration:
                                      type: number
                                      description: Audio duration in seconds
                                      examples:
                                        - 339.8
                                    audio_url:
                                      type: string
                                      format: uri
                                      description: URL of the separated audio track
                                      examples:
                                        - https://example.mp3
                                    stem_type_group_name:
                                      type: string
                                      description: >-
                                        Name of the stem type group (e.g.,
                                        Vocals, Instrumental, Drums, Bass, etc.)
                                      examples:
                                        - Vocals
                                    id:
                                      type: string
                                      description: >-
                                        Unique identifier for the audio track.
                                        This ID can be used as audioId parameter
                                        in MIDI generation.
                                      examples:
                                        - 8ca376e7-2693-48d2-875d-08aaf2c6dd27
                                  x-apidog-orders:
                                    - duration
                                    - audio_url
                                    - stem_type_group_name
                                    - id
                                  x-apidog-ignore-properties: []
                              instrumentalUrl:
                                type: string
                                description: >-
                                  Instrumental part audio URL (separate_vocal
                                  type only)
                              vocalUrl:
                                type: string
                                description: Vocal part audio URL
                              backingVocalsUrl:
                                type: string
                                description: >-
                                  Backing vocals audio URL (split_stem type
                                  only)
                              drumsUrl:
                                type: string
                                description: Drums part audio URL (split_stem type only)
                              bassUrl:
                                type: string
                                description: Bass part audio URL (split_stem type only)
                              guitarUrl:
                                type: string
                                description: Guitar part audio URL (split_stem type only)
                              pianoUrl:
                                type: string
                                description: Piano part audio URL (split_stem type only)
                              keyboardUrl:
                                type: string
                                description: Keyboard part audio URL (split_stem type only)
                              percussionUrl:
                                type: string
                                description: >-
                                  Percussion part audio URL (split_stem type
                                  only)
                              stringsUrl:
                                type: string
                                description: Strings part audio URL (split_stem type only)
                              synthUrl:
                                type: string
                                description: >-
                                  Synthesizer part audio URL (split_stem type
                                  only)
                              fxUrl:
                                type: string
                                description: Effects part audio URL (split_stem type only)
                              brassUrl:
                                type: string
                                description: Brass part audio URL (split_stem type only)
                              woodwindsUrl:
                                type: string
                                description: >-
                                  Woodwinds part audio URL (split_stem type
                                  only)
                            x-apidog-orders:
                              - id
                              - originUrl
                              - originData
                              - instrumentalUrl
                              - vocalUrl
                              - backingVocalsUrl
                              - drumsUrl
                              - bassUrl
                              - guitarUrl
                              - pianoUrl
                              - keyboardUrl
                              - percussionUrl
                              - stringsUrl
                              - synthUrl
                              - fxUrl
                              - brassUrl
                              - woodwindsUrl
                            x-apidog-ignore-properties: []
                          successFlag:
                            type: string
                            description: Task status
                            enum:
                              - PENDING
                              - SUCCESS
                              - CREATE_TASK_FAILED
                              - GENERATE_AUDIO_FAILED
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
              examples:
                separate_vocal:
                  summary: separate_vocal Type Query Result
                  value:
                    code: 200
                    msg: success
                    data:
                      taskId: 3e63b4cc88d52611159371f6af5571e7
                      musicId: 376c687e-d439-42c1-b1e4-bcb43b095ec2
                      callbackUrl: >-
                        https://57312fc2e366.ngrok-free.app/api/v1/vocal-removal/test
                      musicIndex: 0
                      completeTime: 1753782937000
                      response:
                        id: null
                        originUrl: null
                        originData:
                          - duration: 245.6
                            audio_url: https://example001.mp3
                            stem_type_group_name: Vocals
                            id: 3d7021c9-fa8b-4eda-91d1-3b9297ddb172
                          - duration: 245.6
                            audio_url: https://example002.mp3
                            stem_type_group_name: Instrumental
                            id: d92a13bf-c6f4-4ade-bb47-f69738435528
                        instrumentalUrl: >-
                          https://file.aiquickdraw.com/s/d92a13bf-c6f4-4ade-bb47-f69738435528_Instrumental.mp3
                        vocalUrl: >-
                          https://file.aiquickdraw.com/s/3d7021c9-fa8b-4eda-91d1-3b9297ddb172_Vocals.mp3
                        backingVocalsUrl: null
                        drumsUrl: null
                        bassUrl: null
                        guitarUrl: null
                        pianoUrl: null
                        keyboardUrl: null
                        percussionUrl: null
                        stringsUrl: null
                        synthUrl: null
                        fxUrl: null
                        brassUrl: null
                        woodwindsUrl: null
                      successFlag: SUCCESS
                      createTime: 1753782854000
                      errorCode: null
                      errorMessage: null
                split_stem:
                  summary: split_stem Type Query Result
                  value:
                    code: 200
                    msg: success
                    data:
                      taskId: e649edb7abfd759285bd41a47a634b10
                      musicId: 376c687e-d439-42c1-b1e4-bcb43b095ec2
                      callbackUrl: >-
                        https://57312fc2e366.ngrok-free.app/api/v1/vocal-removal/test
                      musicIndex: 0
                      completeTime: 1753782459000
                      response:
                        id: null
                        originUrl: null
                        originData:
                          - duration: 312.4
                            audio_url: https://example001.mp3
                            stem_type_group_name: Keyboard
                            id: adc934e0-fa7d-45da-da20-1dba160d74e0
                          - duration: 312.4
                            audio_url: https://example002.mp3
                            stem_type_group_name: Percussion
                            id: 0f70884d-047c-41f1-a6d0-7023js8b7dc6
                          - duration: 312.4
                            audio_url: https://example003.mp3
                            stem_type_group_name: Strings
                            id: 49829425-a5b0-424e-857a-75d4233a426b
                          - duration: 312.4
                            audio_url: https://example004.mp3
                            stem_type_group_name: Synth
                            id: 56b2d94a-eb92-4d21-bc43-346024we8348
                        instrumentalUrl: null
                        vocalUrl: >-
                          https://file.aiquickdraw.com/s/07420749-29a2-4054-9b62-e6a6f8b90ccb_Vocals.mp3
                        backingVocalsUrl: >-
                          https://file.aiquickdraw.com/s/aadc51a3-4c88-4c8e-a4c8-e867c539673d_Backing_Vocals.mp3
                        drumsUrl: >-
                          https://file.aiquickdraw.com/s/ac75c5ea-ac77-4ad2-b7d9-66e140b78e44_Drums.mp3
                        bassUrl: >-
                          https://file.aiquickdraw.com/s/a3c2da5a-b364-4422-adb5-2692b9c26d33_Bass.mp3
                        guitarUrl: >-
                          https://file.aiquickdraw.com/s/064dd08e-d5d2-4201-9058-c5c40fb695b4_Guitar.mp3
                        pianoUrl: null
                        keyboardUrl: >-
                          https://file.aiquickdraw.com/s/adc934e0-df7d-45da-8220-1dba160d74e0_Keyboard.mp3
                        percussionUrl: >-
                          https://file.aiquickdraw.com/s/0f70884d-047c-41f1-a6d0-7044618b7dc6_Percussion.mp3
                        stringsUrl: >-
                          https://file.aiquickdraw.com/s/49829425-a5b0-424e-857a-75d4c63a426b_Strings.mp3
                        synthUrl: >-
                          https://file.aiquickdraw.com/s/56b2d94a-eb92-4d21-bc43-3460de0c8348_Synth.mp3
                        fxUrl: >-
                          https://file.aiquickdraw.com/s/a8822c73-6629-4089-8f2a-d19f41f0007d_FX.mp3
                        brassUrl: >-
                          https://file.aiquickdraw.com/s/334b2d23-0c65-4a04-92c7-22f828afdd44_Brass.mp3
                        woodwindsUrl: >-
                          https://file.aiquickdraw.com/s/d81545b1-6f94-4388-9785-1aaa6ecabb02_Woodwinds.mp3
                      successFlag: SUCCESS
                      createTime: 1753782327000
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
      x-apidog-folder: docs/en/Market/Suno API/Vocal Removal
      x-apidog-status: released
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506301-run
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
