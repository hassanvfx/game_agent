# Get 4K Video Callbacks


> When 4K video generation completes, the system calls this callback to notify results.

:::info[Overview]
When the 4K video generation task completes, the system will notify you of the results through the callback mechanism.
:::

:::tip[]
  **Webhook Security**: To ensure the authenticity and integrity of callback requests, we strongly recommend implementing webhook signature verification. See our [Webhook Verification Guide](/common-api/webhook-verification) for detailed implementation steps.
:::

### Callback Configuration

Configure the callback URL when requesting 4K video generation:

```json
{
  "taskId": "veo_task_abcdef123456",
  "index": 0,
  "callBackUrl": "https://your-domain.com/api/4k-callback"
}
```

---

### Callback Format

When 4K video generation completes, the system will send a **POST** request to your configured callback URL.

#### 1. Success Callback Result
```json
{
  "code": 200,
  "msg": "4K Video generated successfully.",
  "data": {
    "taskId": "veo_task_example123",
    "info": {
      "resultUrls": [
        "https://file.aiquickdraw.com/v/example_task_1234567890.mp4"
      ],
      "imageUrls": [
        "https://file.aiquickdraw.com/v/example_task_1234567890.jpg"
      ]
    }
  }
}
```

#### 2. Failure Callback Result
```json
{
  "code": 500,
  "msg": "The 4K version of this video is unavailable. Please try a different video.",
  "data": {
    "taskId": "veo_task_abcdef123456"
  }
}
```

---

### Callback Field Descriptions

| Field | Type | Description |
| :--- | :--- | :--- |
| **code** | integer | Status code. `200`: Success; `500`: Failure. |
| **msg** | string | Status message or error description. |
| **data** | object | Task result data when successful. |
| ∟ **taskId** | string | The unique task identifier. |
| ∟ **info.resultUrls** | array | Generated 4K video download URL array. |
| ∟ **info.imageUrls** | array | Related thumbnail or preview image URL array. |

---

### Callback Handling Process

1.  **Verify Callback**: Check the `code` field to confirm generation success.
2.  **Extract Results**: Retrieve the generated 4K video download address from `data.info.resultUrls`.
3.  **Respond to Callback**: Your server should return a `200` status code to confirm callback receipt.

---

### Error Handling

If errors occur during 4K video generation, the callback will return an error status code with the corresponding error message:

*   **500**: 4K version unavailable — *"The 4K version of this video is unavailable. Please try a different video."*

:::warning[]
Ensure your callback endpoint can handle duplicate callbacks (idempotency) to avoid processing the same task multiple times.
:::

---

## Best Practices

:::tip[Recommendations]
- **Timely Download**: 4K files are large and URLs may expire. Save them to your own storage promptly.
- **Idempotent Processing**: The same task may trigger multiple callbacks; ensure your logic handles this.
- **Media Management**: Use the returned `taskId` for media file tracking.
- **Storage Planning**: 4K video files are typically very large; ensure sufficient disk space.
:::

---

## Alternative Solutions

If you cannot use the callback mechanism, you can also use polling:

<Card title="Poll Query Results" icon="lucide-radar" href="/veo3-api/get-veo-3-video-details">
  Use the Get Video Details endpoint to periodically query 4K video generation task status.
</Card>

---

If you encounter any issues during usage, please contact our technical support: [support@kie.ai](mailto:support@kie.ai)

