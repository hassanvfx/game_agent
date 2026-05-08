# Music Generation Callbacks

System will call this callback when audio generation is complete.

When you submit a music generation task to the Suno API, you can use the `callBackUrl` parameter to set a callback URL. The system will automatically push the results to your specified address when the task is completed.

## Callback Mechanism Overview

:::info[]
The callback mechanism eliminates the need to poll the API for task status. The system will proactively push task completion results to your server.
:::

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Timing

The system will send callback notifications in the following situations:
- Music generation task completed successfully
- Music generation task failed
- Errors occurred during task processing

### Callback Method

- **HTTP Method**: POST
- **Content Type**: application/json
- **Timeout Setting**: 15 seconds

## Callback Request Format

When the task is completed, the system will send a POST request to your `callBackUrl` in the following format:

<Tabs>
  <TabItem value="success" label="Success Callback">
    ```json
    {
      "code": 200,
      "msg": "All generated successfully.",
      "data": {
        "callbackType": "complete",
        "task_id": "2fac****9f72",
        "data": [
          {
            "id": "e231****-****-****-****-****8cadc7dc",
            "audio_url": "https://example.cn/****.mp3",
            "stream_audio_url": "https://example.cn/****",
            "image_url": "https://example.cn/****.jpeg",
            "prompt": "[Verse] Night city lights shining bright",
            "model_name": "chirp-v3-5",
            "title": "Iron Man",
            "tags": "electrifying, rock",
            "createTime": "2025-01-01 00:00:00",
            "duration": 198.44
          },
          {
            "id": "e231****-****-****-****-****8cadc7dc",
            "audio_url": "https://example.cn/****.mp3",
            "stream_audio_url": "https://example.cn/****",
            "image_url": "https://example.cn/****.jpeg",
            "prompt": "[Verse] Night city lights shining bright",
            "model_name": "chirp-v3-5",
            "title": "Iron Man",
            "tags": "electrifying, rock",
            "createTime": "2025-01-01 00:00:00",
            "duration": 228.28
          }
        ]
      }
    }
    ```
  </TabItem>
  <TabItem value="failure" label="Failure Callback">
    ```json
    {
      "code": 501,
      "msg": "Audio generation failed",
      "data": {
        "callbackType": "error",
        "task_id": "2fac****9f72",
        "data": null
      }
    }
    ```
  </TabItem>
</Tabs>

## Status Code Description

### code (integer, required)

Callback status code indicating task processing result:

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Request has been processed successfully |
| 400 | Validation Error - Lyrics contained copyrighted material |
| 408 | Rate Limited - Timeout |
| 413 | Conflict - Uploaded audio matches existing work of art |
| 500 | Server Error - An unexpected error occurred while processing the request |
| 501 | Audio generation failed |
| 531 | Server Error - Sorry, the generation failed due to an issue. Your credits have been refunded. Please try again |

### msg (string, required)

Status message providing detailed status description

### data.callbackType (string, required)

Callback type:
- **text** - Text generation complete
- **first** - First track complete
- **complete** - All tracks complete
- **error** - Generation failed

### data.task_id (string, required)

Task ID, consistent with the task_id returned when you submitted the task

### data.data (array)

Generated audio data array, returned on success

### data.data[].id (string)

Audio unique identifier (audioId)

### data.data[].audio_url (string)

Audio file URL

### data.data[].stream_audio_url (string)

Streaming audio URL

### data.data[].image_url (string)

Cover image URL

### data.data[].prompt (string)

Generation prompt/lyrics

### data.data[].model_name (string)

Model name used

### data.data[].title (string)

Music title

### data.data[].tags (string)

Music tags

### data.data[].createTime (string)

Creation time

### data.data[].duration (number)

Audio duration (seconds)

## Callback Reception Examples

Here are example codes for receiving callbacks in popular programming languages:

<Tabs>
  <TabItem value="nodejs" label="Node.js">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/suno-callback', (req, res) => {
      const { code, msg, data } = req.body;
      
      console.log('Received callback:', {
        taskId: data.task_id,
        status: code,
        message: msg,
        callbackType: data.callbackType
      });
      
      if (code === 200) {
        // Task completed successfully
        if (data.callbackType === 'complete') {
          console.log('Music generation completed:', data.data);
          
          // Process generated music data
          data.data.forEach(audio => {
            console.log(`Audio ID: ${audio.id}`);
            console.log(`Audio URL: ${audio.audio_url}`);
            console.log(`Title: ${audio.title}`);
            console.log(`Duration: ${audio.duration} seconds`);
          });
          
        } else if (data.callbackType === 'first') {
          console.log('First track completed');
          
        } else if (data.callbackType === 'text') {
          console.log('Text generation completed');
        }
        
      } else {
        // Task failed
        console.log('Task failed:', msg);
        
        // Handle failure cases...
      }
      
      // Return 200 status code to confirm callback received
      res.status(200).json({ status: 'received' });
    });

    app.listen(3000, () => {
      console.log('Callback server running on port 3000');
    });
    ```
  </TabItem>

  <TabItem value="python" label="Python">
    ```python
    from flask import Flask, request, jsonify
    import json

    app = Flask(__name__)

    @app.route('/suno-callback', methods=['POST'])
    def handle_callback():
        data = request.json
        
        code = data.get('code')
        msg = data.get('msg')
        callback_data = data.get('data', {})
        task_id = callback_data.get('task_id')
        callback_type = callback_data.get('callbackType')
        
        print(f"Received callback: {task_id}, status: {code}, type: {callback_type}, message: {msg}")
        
        if code == 200:
            # Task completed successfully
            if callback_type == 'complete':
                audio_list = callback_data.get('data', [])
                print(f"Music generation completed, generated {len(audio_list)} tracks")
                
                for audio in audio_list:
                    print(f"Audio ID: {audio['id']}")
                    print(f"Audio URL: {audio['audio_url']}")
                    print(f"Title: {audio['title']}")
                    print(f"Duration: {audio['duration']} seconds")
                    
            elif callback_type == 'first':
                print("First track completed")
                
            elif callback_type == 'text':
                print("Text generation completed")
                
        else:
            # Task failed
            print(f"Task failed: {msg}")
            
            # Handle failure cases...
        
        # Return 200 status code to confirm callback received
        return jsonify({'status': 'received'}), 200

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=3000)
    ```
  </TabItem>

  <TabItem value="php" label="PHP">
    ```php
    <?php
    header('Content-Type: application/json');

    // Get POST data
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    $code = $data['code'] ?? null;
    $msg = $data['msg'] ?? '';
    $callbackData = $data['data'] ?? [];
    $taskId = $callbackData['task_id'] ?? '';
    $callbackType = $callbackData['callbackType'] ?? '';

    error_log("Received callback: $taskId, status: $code, type: $callbackType, message: $msg");

    if ($code === 200) {
        // Task completed successfully
        if ($callbackType === 'complete') {
            $audioList = $callbackData['data'] ?? [];
            error_log("Music generation completed, generated " . count($audioList) . " tracks");
            
            foreach ($audioList as $audio) {
                error_log("Audio ID: " . $audio['id']);
                error_log("Audio URL: " . $audio['audio_url']);
                error_log("Title: " . $audio['title']);
                error_log("Duration: " . $audio['duration'] . " seconds");
            }
            
        } elseif ($callbackType === 'first') {
            error_log("First track completed");
            
        } elseif ($callbackType === 'text') {
            error_log("Text generation completed");
        }
        
    } else {
        // Task failed
        error_log("Task failed: $msg");
        
        // Handle failure cases...
    }

    // Return 200 status code to confirm callback received
    http_response_code(200);
    echo json_encode(['status' => 'received']);
    ?>
    ```
  </TabItem>
</Tabs>

## Best Practices

:::tip Callback URL Configuration Recommendations
1. **Use HTTPS**: Ensure your callback URL uses HTTPS protocol for secure data transmission
2. **Verify Source**: Verify the legitimacy of the request source in callback processing
3. **Idempotent Processing**: The same task_id may receive multiple callbacks, ensure processing logic is idempotent
4. **Quick Response**: Callback processing should return a 200 status code as quickly as possible to avoid timeout
5. **Asynchronous Processing**: Complex business logic should be processed asynchronously to avoid blocking callback response
6. **Stage Tracking**: Differentiate between different generation stages based on callbackType and arrange business logic appropriately
:::

:::warning Important Reminders
- Callback URL must be a publicly accessible address
- Server must respond within 15 seconds, otherwise it will be considered a timeout
- If 3 consecutive retries fail, the system will stop sending callbacks
- Please ensure the stability of callback processing logic to avoid callback failures due to exceptions
- Pay attention to handling different callbackType callbacks, especially the complete type for final results
:::

## Troubleshooting

If you do not receive callback notifications, please check the following:

<details>
  <summary>Network Connection Issues</summary>

- Confirm that the callback URL is accessible from the public network
- Check firewall settings to ensure inbound requests are not blocked
- Verify that domain name resolution is correct
</details>

<details>
  <summary>Server Response Issues</summary>

- Ensure the server returns HTTP 200 status code within 15 seconds
- Check server logs for error messages
- Verify that the interface path and HTTP method are correct
</details>

<details>
  <summary>Content Format Issues</summary>

- Confirm that the received POST request body is in JSON format
- Check that Content-Type is application/json
- Verify that JSON parsing is correct
</details>

<details>
  <summary>Callback Type Processing</summary>

- Confirm proper handling of different callbackTypes
- Check if processing of complete type final results is missed
- Verify that audio data parsing is correct
</details>

## Alternative Solution

If you cannot use the callback mechanism, you can also use polling:

<Card
  title="Poll Query Results"
  icon="lucide-radar"
  href="/suno-api/get-music-details"
>
  Use the get music details endpoint to regularly query task status. We recommend querying every 30 seconds.
</Card>

