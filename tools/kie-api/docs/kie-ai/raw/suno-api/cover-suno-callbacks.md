# Music Cover Generation Callbacks

When music cover generation is complete, the system will call this callback to notify results.

When you submit a cover generation task to the Suno API, you can use the `callBackUrl` parameter to set the callback URL. When the task is complete, the system will automatically push results to your specified address.

## Callback Mechanism Overview

:::info[]
The callback mechanism eliminates the need to poll the API for task status. The system will actively push task completion results to your server.
:::

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Timing

The system will send callback notifications in the following situations:
- Cover generation task completed successfully
- Cover generation task failed
- Error occurred during task processing

### Callback Method

- **HTTP Method**: POST
- **Content Type**: application/json
- **Timeout Setting**: 15 seconds

## Callback Request Format

When the task is complete, the system will send a POST request to your `callBackUrl`:

<Tabs>
  <TabItem value="success" label="Success Callback">
    ```json
    {
      "code": 200,
      "data": {
        "images": [
          "https://tempfile.aiquickdraw.com/s/1753958521_6c1b3015141849d1a9bf17b738ce9347.png",
          "https://tempfile.aiquickdraw.com/s/1753958524_c153143acc6340908431cf0e90cbce9e.png"
        ],
        "taskId": "21aee3c3c2a01fa5e030b3799fa4dd56"
      },
      "msg": "success"
    }
    ```
  </TabItem>
  <TabItem value="failure" label="Failure Callback">
    ```json
    {
      "code": 501,
      "msg": "Cover generation failed",
      "data": {
        "taskId": "21aee3c3c2a01fa5e030b3799fa4dd56",
        "images": null
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
| 200 | Success - Request processed successfully |
| 400 | Validation error - Request parameters invalid |
| 408 | Rate limited - Timeout |
| 500 | Server error - Unexpected error occurred while processing request |
| 501 | Cover generation failed |
| 531 | Server error - Sorry, generation failed due to an issue. Your credits have been refunded. Please try again |

### msg (string, required)

Status message providing more detailed status description

### data.taskId (string, required)

Task ID, consistent with the taskId returned when you submitted the task

### data.images (array)

Array of generated cover image URLs, returned on success. Usually contains 2 different style cover images

## Callback Reception Examples

Here are example codes for receiving callbacks in common programming languages:

<Tabs>
  <TabItem value="nodejs" label="Node.js">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/suno-cover-callback', (req, res) => {
      const { code, msg, data } = req.body;
      
      console.log('Received cover generation callback:', {
        taskId: data.taskId,
        status: code,
        message: msg
      });
      
      if (code === 200) {
        // Task completed successfully
        console.log('Cover generation completed');
        const images = data.images;
        
        if (images && images.length > 0) {
          console.log('Generated cover images:');
          images.forEach((imageUrl, index) => {
            console.log(`Cover ${index + 1}: ${imageUrl}`);
          });
          
          // Process cover images
          // Can download images, save locally, update database, etc.
          downloadImages(images, data.taskId);
        }
        
      } else {
        // Task failed
        console.log('Cover generation failed:', msg);
        
        // Handle failure cases...
      }
      
      // Return 200 status code to confirm callback received
      res.status(200).json({ status: 'received' });
    });

    // Download images function
    async function downloadImages(imageUrls, taskId) {
      const fs = require('fs');
      const path = require('path');
      const https = require('https');
      
      // Create directory
      const dir = `covers/${taskId}`;
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      for (let i = 0; i < imageUrls.length; i++) {
        const url = imageUrls[i];
        const filename = path.join(dir, `cover_${i + 1}.png`);
        
        try {
          await downloadFile(url, filename);
          console.log(`Cover saved: ${filename}`);
        } catch (error) {
          console.error(`Download failed: ${error.message}`);
        }
      }
    }

    function downloadFile(url, filename) {
      return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filename);
        https.get(url, (response) => {
          response.pipe(file);
          file.on('finish', () => {
            file.close();
            resolve();
          });
        }).on('error', (err) => {
          fs.unlink(filename, () => {});
          reject(err);
        });
      });
    }

    app.listen(3000, () => {
      console.log('Callback server running on port 3000');
    });
    ```
  </TabItem>

  <TabItem value="python" label="Python">
    ```python
    from flask import Flask, request, jsonify
    import requests
    import os
    from urllib.parse import urlparse

    app = Flask(__name__)

    @app.route('/suno-cover-callback', methods=['POST'])
    def handle_callback():
        data = request.json
        
        code = data.get('code')
        msg = data.get('msg')
        callback_data = data.get('data', {})
        task_id = callback_data.get('taskId')
        images = callback_data.get('images')
        
        print(f"Received cover generation callback: {task_id}, status: {code}, message: {msg}")
        
        if code == 200:
            # Task completed successfully
            print("Cover generation completed")
            
            if images:
                print("Generated cover images:")
                for i, image_url in enumerate(images, 1):
                    print(f"Cover {i}: {image_url}")
                
                # Download cover images
                download_images(images, task_id)
                
        else:
            # Task failed
            print(f"Cover generation failed: {msg}")
            
            # Handle failure cases...
        
        # Return 200 status code to confirm callback received
        return jsonify({'status': 'received'}), 200

    def download_images(image_urls, task_id):
        """Download cover images"""
        # Create directory
        dir_path = f"covers/{task_id}"
        os.makedirs(dir_path, exist_ok=True)
        
        for i, url in enumerate(image_urls, 1):
            try:
                # Get file extension
                parsed_url = urlparse(url)
                file_ext = os.path.splitext(parsed_url.path)[1] or '.png'
                filename = os.path.join(dir_path, f"cover_{i}{file_ext}")
                
                # Download file
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Cover saved: {filename}")
                else:
                    print(f"Download failed {url}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"Download failed {url}: {e}")

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=3000)
    ```
  </TabItem>

  <TabItem value="java" label="Java">
    ```java
    @PostMapping("/suno-cover-callback")
    public ResponseEntity<Map<String, String>> handleCoverCallback(
        @RequestBody CoverCallbackRequest request) {
        
        log.info("Received cover generation callback: taskId={}, status={}, message={}", 
            request.getData().getTaskId(), request.getCode(), request.getMsg());
    
        try {
            if (request.getCode() == 200) {
                // Task completed successfully
                log.info("Cover generation completed");
                List<String> images = request.getData().getImages();
                
                if (images != null && !images.isEmpty()) {
                    log.info("Generated cover images: {}", images);
                    processCoverImages(request.getData().getTaskId(), images);
                }
                
            } else {
                // Task failed
                log.error("Cover generation failed: {}", request.getMsg());
                handleCoverGenerationFailure(request.getData().getTaskId(), 
                    request.getCode(), request.getMsg());
            }
            
            coverTaskService.updateTaskStatus(request.getData().getTaskId(), 
                request.getCode(), request.getMsg(), request.getData().getImages());
                
        } catch (Exception e) {
            log.error("Failed to process cover generation callback", e);
            return ResponseEntity.status(500)
                .body(Map.of("status", "error", "message", e.getMessage()));
        }
        
        return ResponseEntity.ok(Map.of("status", "received"));
    }

    private void processCoverImages(String taskId, List<String> imageUrls) {
        CompletableFuture.runAsync(() -> {
            try {
                downloadCoverImages(taskId, imageUrls);
            } catch (Exception e) {
                log.error("Failed to download cover images: taskId={}", taskId, e);
            }
        });
    }

    private void downloadCoverImages(String taskId, List<String> imageUrls) {
        String dirPath = "covers/" + taskId;
        File dir = new File(dirPath);
        if (!dir.exists()) {
            dir.mkdirs();
        }
        
        for (int i = 0; i < imageUrls.size(); i++) {
            String url = imageUrls.get(i);
            String filename = dirPath + "/cover_" + (i + 1) + ".png";
            
            try {
                downloadFile(url, filename);
                log.info("Cover saved: {}", filename);
            } catch (Exception e) {
                log.error("Download failed: {}", url, e);
            }
        }
    }

    @Data
    public class CoverCallbackRequest {
        private Integer code;
        private String msg;
        private CoverCallbackData data;
    }

    @Data
    public class CoverCallbackData {
        private String taskId;
        private List<String> images;
    }
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
    $taskId = $callbackData['taskId'] ?? '';
    $images = $callbackData['images'] ?? null;

    error_log("Received cover generation callback: $taskId, status: $code, message: $msg");

    if ($code === 200) {
        // Task completed successfully
        error_log("Cover generation completed");
        
        if ($images && is_array($images) && count($images) > 0) {
            error_log("Generated cover images: " . implode(', ', $images));
            downloadCoverImages($taskId, $images);
        }
        
    } else {
        // Task failed
        error_log("Cover generation failed: $msg");
    }

    function downloadCoverImages($taskId, $imageUrls) {
        $dir = "covers/$taskId";
        if (!is_dir($dir)) {
            mkdir($dir, 0777, true);
        }
        
        foreach ($imageUrls as $index => $url) {
            $filename = $dir . "/cover_" . ($index + 1) . ".png";
            
            try {
                $imageContent = file_get_contents($url);
                if ($imageContent !== false) {
                    file_put_contents($filename, $imageContent);
                    error_log("Cover saved: $filename");
                } else {
                    error_log("Download failed: $url");
                }
            } catch (Exception $e) {
                error_log("Download failed $url: " . $e->getMessage());
            }
        }
    }

    http_response_code(200);
    echo json_encode(['status' => 'received']);
    ?>
    ```
  </TabItem>
</Tabs>

## Best Practices

:::tip Callback URL Configuration Recommendations
1. **Use HTTPS**: Ensure callback URL uses HTTPS protocol for data transmission security
2. **Verify Source**: Verify the legitimacy of request sources in callback processing
3. **Idempotent Processing**: The same taskId may receive multiple callbacks, ensure processing logic is idempotent
4. **Quick Response**: Callback processing should return 200 status code quickly to avoid timeout
5. **Asynchronous Processing**: Complex business logic should be processed asynchronously to avoid blocking callback response
6. **Image Management**: Download and save images promptly, noting URL validity period
7. **Error Retry**: Implement retry mechanism for failed image downloads
:::

:::warning Important Reminders
- Callback URL must be a publicly accessible address
- Server must respond within 15 seconds, otherwise it will be considered timeout
- If 3 consecutive retries fail, the system will stop sending callbacks
- Please ensure stability of callback processing logic to avoid callback failures due to exceptions
- Cover image URLs may have validity periods, recommend downloading and saving promptly
- Usually generates 2 different style cover images for selection
- Note handling exceptions for failed image downloads
:::

## Troubleshooting

If you don't receive callback notifications, please check the following:

<details>
  <summary>Network Connection Issues</summary>

- Confirm callback URL is accessible from the public internet
- Check firewall settings to ensure inbound requests are not blocked
- Verify domain name resolution is correct
</details>

<details>
  <summary>Server Response Issues</summary>

- Ensure server returns HTTP 200 status code within 15 seconds
- Check server logs for error messages
- Verify interface path and HTTP method are correct
</details>

<details>
  <summary>Content Format Issues</summary>

- Confirm received POST request body is in JSON format
- Check if Content-Type is application/json
- Verify JSON parsing is correct
</details>

<details>
  <summary>Image Processing Issues</summary>

- Confirm image URLs are accessible
- Check image download permissions and network connection
- Verify file save path and permissions
- Note image URL validity period limitations
</details>

## Alternative Solutions

If you cannot use the callback mechanism, you can also use polling:

<Card
  title="Poll Query Results"
  icon="lucide-radar"
  href="/suno-api/get-music-details"
>
  Use the get music details endpoint to regularly query task status. We recommend querying every 30 seconds.
</Card>

