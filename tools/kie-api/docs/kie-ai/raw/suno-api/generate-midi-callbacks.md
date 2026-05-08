# MIDI Generation Callbacks

System will call this callback when MIDI generation from separated audio is complete.

When you submit a MIDI generation task to the Suno API, you can use the `callBackUrl` parameter to set a callback URL. The system will automatically push the results to your specified address when the task is completed.

## Callback Mechanism Overview

:::info[]
The callback mechanism eliminates the need to poll the API for task status. The system will proactively push task completion results to your server.
:::

:::tip Webhook Security
To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Timing

The system will send callback notifications in the following situations:
- MIDI generation task completed successfully
- MIDI generation task failed
- Errors occurred during task processing

### Callback Method

- **HTTP Method**: POST
- **Content Type**: application/json
- **Timeout Setting**: 15 seconds

## Callback Request Format

When the task is completed, the system will send a POST request to your `callBackUrl`:

<Tabs>
  <TabItem value="success" label="Success Callback">
    ```json
    {
      "code": 200,
      "msg": "success",
      "data": {
        "taskId": "5c79****be8e",
        "state": "complete",
        "instruments": [
          {
            "name": "Drums",
            "notes": [
              {
                "pitch": 73,
                "start": "0.036458333333333336",
                "end": "0.18229166666666666",
                "velocity": 1
              },
              {
                "pitch": 61,
                "start": 0.046875,
                "end": "0.19270833333333334",
                "velocity": 1
              },
              {
                "pitch": 73,
                "start": 0.1875,
                "end": "0.4895833333333333",
                "velocity": 1
              }
            ]
          },
          {
            "name": "Electric Bass (finger)",
            "notes": [
              {
                "pitch": 44,
                "start": 7.6875,
                "end": "7.911458333333333",
                "velocity": 1
              },
              {
                "pitch": 56,
                "start": 7.6875,
                "end": "7.911458333333333",
                "velocity": 1
              },
              {
                "pitch": 51,
                "start": 7.6875,
                "end": "7.911458333333333",
                "velocity": 1
              }
            ]
          }
        ]
      }
    }
    ```
  </TabItem>
  <TabItem value="failure" label="Failure Callback">
    ```json
    {
      "code": 500,
      "msg": "MIDI generation failed",
      "data": {
        "taskId": "5c79****be8e"
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
| 200 | Success - MIDI generation completed successfully |
| 500 | Internal Error - Please try again or contact support |

### msg (string, required)

Status message providing detailed status description

### taskId (string, required)

Task ID, consistent with the taskId returned when you submitted the task

### data (object)

MIDI generation result information, returned on success

## Success Response Fields

### data.state (string)

Processing state. Value: `complete` when successful

### data.instruments (array)

Array of detected instruments with their MIDI note data

**Instrument Object Properties:**
- **name** (string) — Instrument name (e.g., "Drums", "Electric Bass (finger)", "Acoustic Grand Piano")
- **notes** (array) — Array of MIDI notes for this instrument

**Note Object Properties:**
- **pitch** (integer) — MIDI note number (0-127). Middle C = 60. [MIDI note reference](https://inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies)
- **start** (number | string) — Note start time in seconds from beginning of audio
- **end** (number | string) — Note end time in seconds from beginning of audio
- **velocity** (number) — Note velocity/intensity (0-1 range). 1 = maximum velocity

## Callback Reception Examples

Below are example codes for receiving callbacks in popular programming languages:

<Tabs>
  <TabItem value="nodejs" label="Node.js">
    ```javascript
    const express = require('express');
    const app = express();

    app.use(express.json());

    app.post('/suno-midi-callback', (req, res) => {
      const { code, msg, taskId, data } = req.body;
      
      console.log('Received MIDI generation callback:', {
        taskId: taskId,
        status: code,
        message: msg
      });
      
      if (code === 200) {
        // Task completed successfully
        console.log('MIDI generation completed');
        
        if (data && data.instruments) {
          console.log(`Detected ${data.instruments.length} instruments`);
          
          data.instruments.forEach(instrument => {
            console.log(`\nInstrument: ${instrument.name}`);
            console.log(`  Note count: ${instrument.notes.length}`);
            
            instrument.notes.forEach((note, idx) => {
              if (idx < 3) {
                console.log(`  Note ${idx + 1}: Pitch ${note.pitch}, ` +
                           `Start ${note.start}s, End ${note.end}s, ` +
                           `Velocity ${note.velocity}`);
              }
            });
          });
          
          // processMidiData(taskId, data);
        }
        
      } else {
        console.log('MIDI generation failed:', msg);
      }
      
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

    @app.route('/suno-midi-callback', methods=['POST'])
    def handle_callback():
        data = request.json
        
        code = data.get('code')
        msg = data.get('msg')
        task_id = data.get('taskId')
        callback_data = data.get('data', {})
        
        print(f"Received MIDI generation callback: {task_id}, status: {code}, message: {msg}")
        
        if code == 200:
            print("MIDI generation completed")
            
            if callback_data and 'instruments' in callback_data:
                instruments = callback_data['instruments']
                print(f"Detected {len(instruments)} instruments")
                
                for instrument in instruments:
                    name = instrument.get('name')
                    notes = instrument.get('notes', [])
                    print(f"\nInstrument: {name}")
                    print(f"  Note count: {len(notes)}")
                    
                    for idx, note in enumerate(notes[:3]):
                        print(f"  Note {idx + 1}: Pitch {note['pitch']}, "
                              f"Start {note['start']}s, End {note['end']}s, "
                              f"Velocity {note['velocity']}")
                
                with open(f"midi_{taskId}.json", "w") as f:
                    json.dump(callback_data, f, indent=2)
                print(f"MIDI data saved to midi_{task_id}.json")
                
        else:
            print(f"MIDI generation failed: {msg}")
        
        return jsonify({'status': 'received'}), 200

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=3000)
    ```
  </TabItem>

  <TabItem value="php" label="PHP">
    ```php
    <?php
    header('Content-Type: application/json');

    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    $code = $data['code'] ?? null;
    $msg = $data['msg'] ?? '';
    $taskId = $data['taskId'] ?? '';
    $callbackData = $data['data'] ?? null;

    error_log("Received MIDI generation callback: $taskId, status: $code, message: $msg");

    if ($code === 200) {
        error_log("MIDI generation completed");
        
        if ($callbackData && isset($callbackData['instruments'])) {
            $instruments = $callbackData['instruments'];
            error_log("Detected " . count($instruments) . " instruments");
            
            foreach ($instruments as $instrument) {
                $name = $instrument['name'] ?? '';
                $notes = $instrument['notes'] ?? [];
                error_log("Instrument: $name");
                error_log("  Note count: " . count($notes));
                
                foreach (array_slice($notes, 0, 3) as $idx => $note) {
                    error_log(sprintf(
                        "  Note %d: Pitch %d, Start %ss, End %ss, Velocity %s",
                        $idx + 1,
                        $note['pitch'],
                        $note['start'],
                        $note['end'],
                        $note['velocity']
                    ));
                }
            }
            
            $filename = "midi_$taskId.json";
            file_put_contents($filename, json_encode($callbackData, JSON_PRETTY_PRINT));
            error_log("MIDI data saved to $filename");
        }
        
    } else {
        error_log("MIDI generation failed: $msg");
    }

    http_response_code(200);
    echo json_encode(['status' => 'received']);
    ?>
    ```
  </TabItem>
</Tabs>

## Best Practices

:::tip Callback URL Configuration Recommendations
1. **Use HTTPS**: Ensure callback URL uses HTTPS protocol for secure data transmission
2. **Verify Origin**: Verify the legitimacy of the request source in callback processing
3. **Idempotent Processing**: The same taskId may receive multiple callbacks, ensure processing logic is idempotent
4. **Quick Response**: Callback processing should return 200 status code quickly to avoid timeout
5. **Asynchronous Processing**: Complex business logic (like MIDI file conversion) should be processed asynchronously
6. **Handle Missing Instruments**: Not all instruments may be detected - handle empty or missing instrument arrays gracefully
7. **Store Raw Data**: Save the complete JSON response for future reference and reprocessing
:::

:::warning Important Reminders
- Callback URL must be publicly accessible
- Server must respond within 15 seconds, otherwise will be considered timeout
- If 3 consecutive retry attempts fail, the system will stop sending callbacks
- Please ensure the stability of callback processing logic to avoid callback failures due to exceptions
- MIDI data is retained for 14 days - download and save promptly if needed long-term
- The number and types of instruments detected depends on audio content
- Note times (start/end) may be strings or numbers - handle both types
:::

## Troubleshooting

If you are not receiving callback notifications, please check the following:

<details>
  <summary>Network Connection Issues</summary>

- Confirm callback URL is accessible from public internet
- Check firewall settings to ensure inbound requests are not blocked
- Verify domain name resolution is correct
</details>

<details>
  <summary>Server Response Issues</summary>

- Ensure server returns HTTP 200 status code within 15 seconds
- Check server logs for error messages
- Verify endpoint path and HTTP method are correct
</details>

<details>
  <summary>Content Format Issues</summary>

- Confirm received POST request body is in JSON format
- Check if Content-Type is application/json
- Verify JSON parsing is correct
- Handle both string and number types for timing values
</details>

<details>
  <summary>Data Processing Issues</summary>

- Some instruments may have empty note arrays
- Not all audio will detect all instrument types
- Verify the original vocal separation used `split_stem` type (not `separate_vocal`)
- Check that the source taskId is from a successfully completed separation
</details>

## Alternative Solutions

If you cannot use the callback mechanism, you can also use polling:

    <Card
  title="Poll Query Results"
  icon="lucide-radar"
  href="/suno-api/get-midi-details"
>
Use the Get MIDI Generation Details endpoint to periodically query task status. We recommend querying every 10-30 seconds.
</Card>

