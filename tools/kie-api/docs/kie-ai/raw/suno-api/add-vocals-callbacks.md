# Add Vocals Callbacks

System will call this callback when vocal generation is complete.

When you submit a vocal generation task to the Suno API using the `/api/v1/generate/add-vocals` endpoint, you can use the `callBackUrl` parameter to set a callback URL. The system will automatically push the results to your specified address when the task is completed.

## Related API Endpoint

This callback is triggered by the following API endpoint:

**[Add Vocals API](/suno-api/add-vocals)** — **POST** `/api/v1/generate/add-vocals` - Add vocals to uploaded music files

## Callback Mechanism Overview

:::info[]
The callback mechanism eliminates the need to poll the API for task status. The system will proactively push task completion results to your server.
:::

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Timing

The system will send callback notifications in the following situations:
- Text generation completed (callbackType: "text")
- First audio track generation completed (callbackType: "first")
- All audio tracks generation completed (callbackType: "complete")
- Vocal generation task failed
- Errors occurred during task processing

### Callback Method

- **HTTP Method**: POST
- **Content Type**: application/json
- **Timeout Setting**: 15 seconds

## Callback Request Format

When the task progresses or completes, the system will send a POST request to your `callBackUrl` in the following format:

<Tabs>
  <TabItem value="complete" label="Complete Success Callback">
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
            "model_name": "chirp-v4-5",
            "title": "Iron Man",
            "createTime": "2025-01-01 00:00:00",
            "duration": 198.44
          }
        ]
      }
    }
    ```
  </TabItem>
  <TabItem value="first" label="First Track Success Callback">
    ```json
    {
      "code": 200,
      "msg": "First track generated successfully.",
      "data": {
        "callbackType": "first",
        "task_id": "2fac****9f72",
        "data": [
          {
            "id": "e231****-****-****-****-****8cadc7dc",
            "audio_url": "https://example.cn/****.mp3",
            "stream_audio_url": "https://example.cn/****",
            "image_url": "https://example.cn/****.jpeg",
            "prompt": "[Verse] Night city lights shining bright",
            "model_name": "chirp-v4-5",
            "title": "Iron Man",
            "createTime": "2025-01-01 00:00:00",
            "duration": 198.44
          }
        ]
      }
    }
    ```
  </TabItem>
  <TabItem value="text" label="Text Generation Callback">
    ```json
    {
      "code": 200,
      "msg": "Text generation completed successfully.",
      "data": {
        "callbackType": "text",
        "task_id": "2fac****9f72",
        "data": []
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

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Request has been processed successfully |
| 400 | Validation Error - Lyrics contained copyrighted material |
| 408 | Rate Limited - Timeout |
| 413 | Conflict - Uploaded audio matches existing work of art |
| 500 | Server Error - An unexpected error occurred while processing the request |
| 501 | Audio generation failed |
| 531 | Server Error - Sorry, the generation failed due to an issue. Your credits have been refunded. Please try again |

## Callback Reception Examples

Here are example codes for receiving callbacks in popular programming languages:

<Tabs>
  <TabItem value="nodejs" label="Node.js">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/vocals-callback', (req, res) => {
      const { code, msg, data } = req.body;
      
      console.log('Received vocals callback:', {
        taskId: data.task_id,
        status: code,
        message: msg,
        callbackType: data.callbackType
      });
      
      if (code === 200) {
        // Task completed successfully
        if (data.callbackType === 'complete') {
          console.log('Vocals generation completed:', data.data);
          
          // Process generated vocals data
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
      }
      
      // Return 200 status code to confirm callback received
      res.status(200).json({ status: 'received' });
    });

    app.listen(3000, () => {
      console.log('Vocals callback server running on port 3000');
    });
    ```
  </TabItem>

  <TabItem value="python" label="Python">
    ```python
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route('/vocals-callback', methods=['POST'])
    def handle_callback():
        data = request.json
        
        code = data.get('code')
        msg = data.get('msg')
        callback_data = data.get('data', {})
        task_id = callback_data.get('task_id')
        callback_type = callback_data.get('callbackType')
        
        print(f"Received vocals callback: {task_id}, status: {code}, type: {callback_type}")
        
        if code == 200:
            # Task completed successfully
            if callback_type == 'complete':
                audio_list = callback_data.get('data', [])
                print(f"Vocals generation completed, generated {len(audio_list)} tracks")
                
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

    error_log("Received vocals callback: $taskId, status: $code, type: $callbackType");

    if ($code === 200) {
        // Task completed successfully
        if ($callbackType === 'complete') {
            $audioList = $callbackData['data'] ?? [];
            error_log("Vocals generation completed, generated " . count($audioList) . " tracks");
            
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

## Alternative Solution

If you cannot use the callback mechanism, you can also use polling:

<Card
  title="Poll Query Results"
  icon="lucide-radar"
  href="/suno-api/get-music-details"
>
  Use the get music details endpoint to regularly query task status. We recommend querying every 30 seconds.
</Card>

