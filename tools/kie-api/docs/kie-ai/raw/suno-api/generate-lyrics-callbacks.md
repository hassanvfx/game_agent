# Lyrics Generation Callbacks

System will call this callback when lyrics generation is complete.

When you submit a lyrics generation task to the Suno API, you can use the `callBackUrl` parameter to set a callback URL. The system will automatically push the results to your specified address when the task is completed.

## Callback Mechanism Overview

:::info[]
The callback mechanism eliminates the need to poll the API for task status. The system will proactively push task completion results to your server.
:::

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Timing

The system will send callback notifications in the following situations:
- Lyrics generation task completed successfully
- Lyrics generation task failed
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
        "task_id": "3b66882fde0a5d398bd269cab6d9542b",
        "data": [
          {
            "error_message": "",
            "status": "complete",
            "text": "[Verse]\nMoonlight spreads across the windowsill\nStars dance, never standing still\nNight breeze weaves dreams with gentle skill\nLeaving all worries on the hill\n\n[Verse 2]\nLights reflect in your bright eyes\nLike meteors across the skies\nThe world stops in that moment's prize\nChasing future, no goodbyes\n\n[Chorus]\nIn starry dreams we find tomorrow\nBreak free from ordinary sorrow\nAll our dreams will bloom and follow\nDon't fear the path, don't fear tomorrow",
            "title": "Starry Night Dreams"
          }
        ]
      }
    }
    ```
  </TabItem>
  <TabItem value="failure" label="Failure Callback">
    ```json
    {
      "code": 400,
      "msg": "Song Description flagged for moderation",
      "data": {
        "callbackType": "complete",
        "task_id": "3b66882fde0a5d398bd269cab6d9542b",
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
| 400 | Please try rephrasing with more specific details or using a different approach |
| 500 | Internal Error - Please try again later |

### msg (string, required)

Status message providing detailed status description

### data.callbackType (string, required)

Callback type, fixed as complete

### data.task_id (string, required)

Task ID, consistent with the task_id returned when you submitted the task

### data.data (array, required)

Generated lyrics list

### data.data[].text (string)

Lyrics content, returns complete lyrics text on success

### data.data[].title (string)

Lyrics title

### data.data[].status (string, required)

Generation status:
- **complete** - Generation successful
- **failed** - Generation failed

### data.data[].error_message (string)

Error message, valid when status is failed

## Callback Reception Examples

Here are example codes for receiving callbacks in popular programming languages:

<Tabs>
  <TabItem value="nodejs" label="Node.js">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/suno-lyrics-callback', (req, res) => {
      const { code, msg, data } = req.body;
      
      console.log('Received lyrics callback:', {
        taskId: data.task_id,
        status: code,
        message: msg,
        callbackType: data.callbackType
      });
      
      if (code === 200) {
        // Task completed successfully
        console.log('Lyrics generation completed:', data.data);
        
        // Process generated lyrics data
        data.data.forEach(lyrics => {
          if (lyrics.status === 'complete') {
            console.log(`Lyrics title: ${lyrics.title}`);
            console.log(`Lyrics content: ${lyrics.text}`);
          } else if (lyrics.status === 'failed') {
            console.log(`Lyrics generation failed: ${lyrics.error_message}`);
          }
        });
        
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

    @app.route('/suno-lyrics-callback', methods=['POST'])
    def handle_callback():
        data = request.json
        
        code = data.get('code')
        msg = data.get('msg')
        callback_data = data.get('data', {})
        task_id = callback_data.get('task_id')
        callback_type = callback_data.get('callbackType')
        
        print(f"Received lyrics callback: {task_id}, status: {code}, type: {callback_type}, message: {msg}")
        
        if code == 200:
            # Task completed successfully
            lyrics_list = callback_data.get('data', [])
            print(f"Lyrics generation completed, generated {len(lyrics_list)} lyrics")
            
            for lyrics in lyrics_list:
                if lyrics['status'] == 'complete':
                    print(f"Lyrics title: {lyrics['title']}")
                    print(f"Lyrics content: {lyrics['text']}")
                elif lyrics['status'] == 'failed':
                    print(f"Lyrics generation failed: {lyrics['error_message']}")
                    
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

    error_log("Received lyrics callback: $taskId, status: $code, type: $callbackType, message: $msg");

    if ($code === 200) {
        // Task completed successfully
        $lyricsList = $callbackData['data'] ?? [];
        error_log("Lyrics generation completed, generated " . count($lyricsList) . " lyrics");
        
        foreach ($lyricsList as $lyrics) {
            if ($lyrics['status'] === 'complete') {
                error_log("Lyrics title: " . $lyrics['title']);
                error_log("Lyrics content: " . $lyrics['text']);
            } elseif ($lyrics['status'] === 'failed') {
                error_log("Lyrics generation failed: " . $lyrics['error_message']);
            }
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
6. **Status Checking**: Check the status field of each lyrics item to distinguish between success and failure cases
:::

:::warning Important Reminders
- Callback URL must be a publicly accessible address
- Server must respond within 15 seconds, otherwise it will be considered a timeout
- If 3 consecutive retries fail, the system will stop sending callbacks
- Please ensure the stability of callback processing logic to avoid callback failures due to exceptions
- Pay attention to handling lyrics generation failure cases, check the error_message field for specific error information
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
  <summary>Lyrics Processing Issues</summary>

- Confirm proper handling of lyrics status field
- Check if processing of failed status lyrics is missed
- Verify that lyrics content parsing is correct
</details>

## Alternative Solution

If you cannot use the callback mechanism, you can also use polling:

<Card
  title="Poll Query Results"
  icon="lucide-radar"
  href="/suno-api/get-lyrics-details"
>
 Use the get lyrics details endpoint to regularly query task status. We recommend querying every 30 seconds.
</Card>
