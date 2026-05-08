# Replace Music Section Callbacks

Understand the callback mechanism for replace music section tasks.

When you submit a replace music section task to the API, you can provide a `callBackUrl` to receive real-time notifications about task progress and completion.

## Callback Mechanism

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### When Callbacks Are Sent

The system sends callbacks at the following times:
- **Complete**: When the replacement task is fully completed

### Callback Method

- **HTTP Method**: POST
- **Content-Type**: application/json
- **Timeout**: 10 seconds
- **Retry Policy**: Up to 3 attempts with exponential backoff

## Request Format

### Success Callback

When the replacement task completes successfully:

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
        "prompt": "A calm and relaxing piano track.",
        "model_name": "chirp-v3-5",
        "title": "Relaxing Piano",
        "tags": "Jazz",
        "createTime": "2025-01-01 00:00:00",
        "duration": 198.44
      }
    ]
  }
}
```

### Failure Callback

When the replacement task fails:

```json
{
  "code": 501,
  "msg": "Audio generation failed.",
  "data": {
    "callbackType": "error",
    "task_id": "2fac****9f72",
    "error": "Generation failed due to technical issues"
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200  | Success - Task completed successfully |
| 400  | Validation error - Parameter validation failed |
| 408  | Timeout - Request timeout |
| 500  | Server error - Unexpected error occurred |
| 501  | Audio generation failed |
| 531  | Server error - Generation failed, credits refunded |

## Response Fields

### Success Response Fields

**code** (integer, required) — Status code indicating the result of the replacement task

**msg** (string, required) — Status message describing the result

**data** (object, required) — Container for callback data

- **callbackType** (string, required) — Type of callback: `complete` or `error`
- **task_id** (string, required) — The task ID for the replacement request
- **data** (array) — Array of replaced music data (only present on success)
  - **id** (string) — Unique identifier for the music segment
  - **audio_url** (string) — Direct URL to the audio file
  - **stream_audio_url** (string) — Streaming URL for the audio
  - **image_url** (string) — URL to the cover image
  - **prompt** (string) — The prompt used for generating the replacement
  - **model_name** (string) — Name of the AI model used
  - **title** (string) — Title of the music
  - **tags** (string) — Style tags for the music
  - **createTime** (string) — Creation timestamp
  - **duration** (number) — Duration of the audio in seconds

## Implementation Examples

<Tabs>
  <TabItem value="nodejs" label="Node.js (Express)">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/replace-section-callback', (req, res) => {
      const { code, msg, data } = req.body;
      
      console.log('Replace section callback received:', {
        code,
        msg,
        taskId: data.task_id,
        callbackType: data.callbackType
      });
      
      if (code === 200 && data.callbackType === 'complete') {
        // Handle successful replacement
        console.log('Replacement completed successfully');
        data.data.forEach((music, index) => {
          console.log(`Music ${index + 1}:`, {
            id: music.id,
            title: music.title,
            duration: music.duration,
            audioUrl: music.audio_url
          });
        });
      } else {
        // Handle failure
        console.log('Replacement failed:', msg);
      }
      
      // Always respond with success to acknowledge receipt
      res.json({ code: 200, msg: 'success' });
    });

    app.listen(3000, () => {
      console.log('Callback server running on port 3000');
    });
    ```
  </TabItem>

  <TabItem value="python" label="Python (Flask)">
    ```python
    from flask import Flask, request, jsonify
    import logging

    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

    @app.route('/replace-section-callback', methods=['POST'])
    def replace_section_callback():
        data = request.json
        code = data.get('code')
        msg = data.get('msg')
        callback_data = data.get('data', {})
        
        logging.info(f"Replace section callback received: code={code}, msg={msg}")
        
        if code == 200 and callback_data.get('callbackType') == 'complete':
            # Handle successful replacement
            logging.info("Replacement completed successfully")
            music_data = callback_data.get('data', [])
            for i, music in enumerate(music_data):
                logging.info(f"Music {i + 1}: {music.get('title')} - {music.get('duration')}s")
        else:
            # Handle failure
            logging.error(f"Replacement failed: {msg}")
        
        # Always respond with success
        return jsonify({"code": 200, "msg": "success"})

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=3000)
    ```
  </TabItem>

  <TabItem value="php" label="PHP">
    ```php
    <?php
    header('Content-Type: application/json');

    // Get the raw POST data
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if ($data === null) {
        http_response_code(400);
        echo json_encode(['code' => 400, 'msg' => 'Invalid JSON']);
        exit;
    }

    $code = $data['code'] ?? null;
    $msg = $data['msg'] ?? '';
    $callbackData = $data['data'] ?? [];

    error_log("Replace section callback received: code=$code, msg=$msg");

    if ($code === 200 && ($callbackData['callbackType'] ?? '') === 'complete') {
        // Handle successful replacement
        error_log("Replacement completed successfully");
        $musicData = $callbackData['data'] ?? [];
        foreach ($musicData as $index => $music) {
            $title = $music['title'] ?? 'Unknown';
            $duration = $music['duration'] ?? 0;
            error_log("Music " . ($index + 1) . ": $title - {$duration}s");
        }
    } else {
        // Handle failure
        error_log("Replacement failed: $msg");
    }

    // Always respond with success
    echo json_encode(['code' => 200, 'msg' => 'success']);
    ?>
    ```
  </TabItem>
</Tabs>

## Callback Security

### Verification Recommendations

1. **IP Whitelist**: Restrict callback endpoints to known IP addresses
2. **HTTPS Only**: Always use HTTPS for callback URLs in production
3. **Request Validation**: Validate the structure and content of callback requests
4. **Timeout Handling**: Implement proper timeout handling for callback processing

### Example Security Implementation

```javascript
const crypto = require('crypto');

function verifyCallback(req, res, next) {
  // Verify request structure
  const { code, msg, data } = req.body;
  if (typeof code !== 'number' || typeof msg !== 'string' || !data) {
    return res.status(400).json({ code: 400, msg: 'Invalid callback format' });
  }
  
  // Verify task ID format
  const taskId = data.task_id;
  if (!taskId || !/^[a-f0-9\*]{12}$/.test(taskId)) {
    return res.status(400).json({ code: 400, msg: 'Invalid task ID' });
  }
  
  next();
}

app.post('/replace-section-callback', verifyCallback, (req, res) => {
  // Process verified callback
  // ... callback handling logic
});
```

## Troubleshooting

### Common Issues

**Q: Callbacks are not being received**
- Verify your callback URL is publicly accessible
- Check that your server is responding within 10 seconds
- Ensure your endpoint accepts POST requests with JSON content

**Q: Receiving duplicate callbacks**
- This can happen due to network issues or timeouts
- Implement idempotency using the task_id to handle duplicates

**Q: Callback data is missing or incomplete**
- Check the `callbackType` field to understand the callback stage
- For error callbacks, check the error message for details

**Q: How to handle callback failures?**
- Always return a 200 status code to acknowledge receipt
- Use the [Get Music Details](/suno-api/get-music-details) endpoint to poll task status as a fallback

### Best Practices

1. **Always Acknowledge**: Return HTTP 200 even if your processing fails
2. **Implement Retry Logic**: Handle temporary failures gracefully
3. **Log Everything**: Keep detailed logs for debugging
4. **Use Fallback Polling**: Don't rely solely on callbacks for critical workflows
5. **Validate Data**: Always validate callback data before processing

