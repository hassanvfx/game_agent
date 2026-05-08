# Get MIDI Generation Details

## OpenAPI Specification

```yaml
openapi: 3.0.1
info:
  title: ''
  description: ''
  version: 1.0.0
paths:
  /api/v1/midi/record-info:
    get:
      summary: Get MIDI Generation Details
      deprecated: false
      description: >-
        Retrieve detailed information about a MIDI generation task including
        complete note data for all detected instruments.


        ### Usage Guide

        - Use this endpoint to check the status of a MIDI generation task

        - Access complete MIDI note data once processing is complete

        - Retrieve detailed instrument and note information

        - Track processing progress and any errors that may have occurred


        ### Status Descriptions

        - `successFlag: 0`: Pending - Task is waiting to be executed

        - `successFlag: 1`: Success - MIDI generation completed successfully

        - `successFlag: 2`: Failed - Failed to create task

        - `successFlag: 3`: Failed - MIDI generation failed

        - Check errorCode and errorMessage fields for failure details


        ### Developer Notes

        - The midiData field contains the complete MIDI data as a structured
        object with instruments and notes

        - MIDI data includes all detected instruments with pitch, timing, and
        velocity for each note

        - MIDI generation records are retained for 14 days

        - **Important**: When using vocal separation with `type: split_stem`,
        the midiData may be empty
      operationId: get-midi-details
      tags:
        - docs/en/Market/Suno API/Vocal Removal
      parameters:
        - name: taskId
          in: query
          description: The task ID returned from the MIDI generation request
          required: true
          example: 5c79****be8e
          schema:
            type: string
      responses:
        '200':
          description: MIDI generation task details retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: Response status code
                    examples:
                      - 200
                  msg:
                    type: string
                    description: Response message
                    examples:
                      - success
                  data:
                    type: object
                    description: MIDI generation task details
                    properties:
                      taskId:
                        type: string
                        description: MIDI generation task ID
                      recordTaskId:
                        type: integer
                        description: Internal record task ID
                      audioId:
                        type: string
                        description: Audio ID from the vocal separation task
                      callbackUrl:
                        type: string
                        description: Callback URL provided when creating the task
                      completeTime:
                        type: integer
                        description: Task completion timestamp (milliseconds)
                      midiData:
                        type: object
                        description: >-
                          Complete MIDI data containing detected instruments and
                          notes
                        properties:
                          state:
                            type: string
                            description: Processing state
                            examples:
                              - complete
                          instruments:
                            type: array
                            description: >-
                              Array of detected instruments with their MIDI
                              notes
                            items:
                              type: object
                              properties:
                                name:
                                  type: string
                                  description: Instrument name
                                notes:
                                  type: array
                                  description: Array of MIDI notes for this instrument
                                  items:
                                    type: object
                                    properties:
                                      pitch:
                                        type: integer
                                        description: MIDI note number (0-127)
                                      start:
                                        type: number
                                        description: Note start time in seconds
                                      end:
                                        type: number
                                        description: Note end time in seconds
                                      velocity:
                                        type: number
                                        description: Note velocity/intensity (0-1)
                                    x-apidog-orders:
                                      - pitch
                                      - start
                                      - end
                                      - velocity
                                    x-apidog-ignore-properties: []
                              x-apidog-orders:
                                - name
                                - notes
                              x-apidog-ignore-properties: []
                        x-apidog-orders:
                          - state
                          - instruments
                        x-apidog-ignore-properties: []
                      successFlag:
                        type: integer
                        description: >-
                          Task status flag: 0 = Pending, 1 = Success, 2 = Failed
                          to create task, 3 = MIDI generation failed
                      createTime:
                        type: integer
                        description: Task creation timestamp (milliseconds)
                      errorCode:
                        type: string
                        description: Error code if task failed
                        nullable: true
                      errorMessage:
                        type: string
                        description: Error message if task failed
                        nullable: true
                    x-apidog-orders:
                      - taskId
                      - recordTaskId
                      - audioId
                      - callbackUrl
                      - completeTime
                      - midiData
                      - successFlag
                      - createTime
                      - errorCode
                      - errorMessage
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
                  taskId: 5c79****be8e
                  recordTaskId: -1
                  audioId: e231****-****-****-****-****8cadc7dc
                  callbackUrl: https://example.callback
                  completeTime: 1760335255000
                  midiData:
                    state: complete
                    instruments:
                      - name: Drums
                        notes:
                          - pitch: 73
                            start: 0.036458333333333336
                            end: 0.18229166666666666
                            velocity: 1
                          - pitch: 61
                            start: 0.046875
                            end: 0.19270833333333334
                            velocity: 1
                      - name: Electric Bass (finger)
                        notes:
                          - pitch: 44
                            start: 7.6875
                            end: 7.911458333333333
                            velocity: 1
                  successFlag: 1
                  createTime: 1760335251000
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
      x-run-in-apidog: https://app.apidog.com/web/project/1184766/apis/api-28506303-run
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
