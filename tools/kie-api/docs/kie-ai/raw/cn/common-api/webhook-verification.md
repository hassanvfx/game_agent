# Webhook 安全校验

:::warning[]
为确保回调请求的安全性，强烈建议在生产环境中启用 Webhook HMAC 签名校验，防止伪造请求和重放攻击。
:::

### 算法说明

Kie AI 使用 **HMAC-SHA256** 算法生成签名，用于验证 Webhook 回调的完整性和真实性。

**签名生成步骤：**

1. **拼接待签名字符串**：`taskId + "." + timestampSeconds`
   - `taskId`：从请求体中获取的任务ID
   - `timestampSeconds`：从 `X-Webhook-Timestamp` 请求头获取的Unix时间戳（秒级）

2. **使用 HMAC-SHA256 计算签名**：
   ```
   signature = HMAC-SHA256(dataToSign, webhookHmacKey)
   ```

3. **Base64 编码**：
   ```
   finalSignature = Base64.encode(signature)
   ```

### 获取 Webhook HMAC Key

您可以在 [Kie AI 设置页面](https://kie.ai/settings) 生成并查看您的 `webhookHmacKey`。

::: info[]
`webhookHmacKey` 用于验证回调请求是否来自 Kie AI 官方服务器。请妥善保管此密钥，切勿泄露或提交到代码仓库。
:::

### Webhook Header 说明
当您在设置页面启用 `webhookHmacKey` 功能后，所有回调请求的 HTTP Header 中将包含以下字段：

### `X-Webhook-Timestamp`
- **类型**： Integer
- **必填**： 是
- **描述**： 回调请求发送时的 Unix 时间戳（秒）。

### `X-Webhook-Signature`
- **类型**： String
- **必填**： 是
- **描述**： 使用 HMAC-SHA256 算法生成的签名，采用 Base64 编码。

#### 签名生成规则：
```
base64(HMAC-SHA256(taskId + "." + timestamp, webhookHmacKey))
```

其中：
- `taskId` 为回调 body 中的任务 ID
- `timestamp` 为 `X-Webhook-Timestamp` 的值
- `webhookHmacKey` 为您在控制台生成的密钥

---

### Webhook 校验流程

请按照以下步骤验证 Webhook 请求的合法性：

<Steps>
<Step title="读取 Header 字段">
从 HTTP Header 中提取 `X-Webhook-Timestamp` 和 `X-Webhook-Signature` 两个字段。

```javascript
const timestamp = req.headers['X-Webhook-Timestamp'];
const receivedSignature = req.headers['X-Webhook-Signature'];
```
</Step>

<Step title="生成签名">
使用本地保存的 `webhookHmacKey`，按照以下规则生成 HMAC-SHA256 签名：

1. 从请求 body 中提取 `task_id`
2. 拼接字符串：`taskId + "." + timestamp`
3. 使用 HMAC-SHA256 算法和 `webhookHmacKey` 生成签名
4. 对签名结果进行 Base64 编码

```javascript
const crypto = require('crypto');

const taskId = req.body.data.task_id;
const message = `${taskId}.${timestamp}`;

const computedSignature = crypto
  .createHmac('sha256', webhookHmacKey)
  .update(message)
  .digest('base64');
```
</Step>

<Step title="对比签名">
将计算出的签名与 `X-Webhook-Signature` 进行对比。使用常量时间比较算法防止时序攻击。

```javascript
// 使用 crypto.timingSafeEqual 进行常量时间比较
if (computedSignature.length !== receivedSignature.length) {
  return res.status(401).json({ error: 'Invalid signature' });
}

const isValid = crypto.timingSafeEqual(
  Buffer.from(computedSignature),
  Buffer.from(receivedSignature)
);

if (isValid) {
  // 签名验证通过，请求合法
  console.log('Webhook signature verified');
} else {
  // 签名验证失败，拒绝请求
  return res.status(401).json({ error: 'Invalid signature' });
}
```

<Check>
如果签名一致，则确认该 Webhook 请求来自 Kie AI 官方服务器，可以安全处理。
</Check>
</Step>
</Steps>

### 完整示例代码

以下是在常用编程语言中实现 Webhook 签名校验的完整示例：

<Tabs>
<Tab title="Node.js">
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

// 从环境变量或配置中读取 webhookHmacKey
const WEBHOOK_HMAC_KEY = process.env.WEBHOOK_HMAC_KEY;

function generateSignature(taskId, timestampSeconds, secret) {
  // 1. 拼接待签名字符串
  const dataToSign = `${taskId}.${timestampSeconds}`;
  
  // 2. 使用 HMAC-SHA256 计算签名
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(dataToSign);
  
  // 3. Base64 编码
  return hmac.digest('base64');
}

function verifySignature(taskId, timestampSeconds, receivedSignature, secret) {
  // 重新生成签名
  const expectedSignature = generateSignature(taskId, timestampSeconds, secret);
  
  // 使用安全的字符串比较
  if (expectedSignature.length !== receivedSignature.length) {
    return false;
  }
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(receivedSignature)
  );
}

function verifyWebhookSignature(req, res, next) {
  // 1. 读取 Header 字段
  const timestamp = req.headers['x-webhook-timestamp'];
  const receivedSignature = req.headers['x-webhook-signature'];

  if (!timestamp || !receivedSignature) {
    return res.status(401).json({ error: 'Missing signature headers' });
  }

  // 2. 验证签名
  const taskId = req.body.data?.task_id;
  if (!taskId) {
    return res.status(400).json({ error: 'Missing task_id' });
  }

  const isValid = verifySignature(taskId, timestamp, receivedSignature, WEBHOOK_HMAC_KEY);
  
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // 签名验证通过
  next();
}

// 应用中间件
app.post('/webhook-callback', verifyWebhookSignature, (req, res) => {
  const { code, msg, data } = req.body;
  
  console.log('收到合法的 Webhook 请求:', {
    taskId: data.task_id,
    status: code,
    callbackType: data.callbackType
  });
  
  // 处理回调数据...
  
  res.status(200).json({ status: 'received' });
});

app.listen(3000, () => {
  console.log('Webhook 服务器运行在端口 3000');
});
```
</Tab>

<Tab title="Python">
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import os

app = Flask(__name__)

# 从环境变量或配置中读取 webhookHmacKey
WEBHOOK_HMAC_KEY = os.getenv('WEBHOOK_HMAC_KEY', '')

def generate_signature(task_id, timestamp_seconds, secret):
    """生成 Webhook 签名"""
    # 1. 拼接待签名字符串
    data_to_sign = f"{task_id}.{timestamp_seconds}"
    
    # 2. 使用 HMAC-SHA256 计算签名
    signature = hmac.new(
        secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # 3. Base64 编码
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(task_id, timestamp_seconds, received_signature, secret):
    """验证 Webhook 签名"""
    # 重新生成签名
    expected_signature = generate_signature(task_id, timestamp_seconds, secret)
    
    # 使用安全的字符串比较
    return hmac.compare_digest(expected_signature, received_signature)

def verify_webhook_signature():
    # 1. 读取 Header 字段
    timestamp = request.headers.get('X-Webhook-Timestamp')
    received_signature = request.headers.get('X-Webhook-Signature')
    
    if not timestamp or not received_signature:
        return False, 'Missing signature headers'
    
    # 2. 验证签名
    data = request.json
    task_id = data.get('data', {}).get('task_id')
    
    if not task_id:
        return False, 'Missing task_id'
    
    is_valid = verify_signature(task_id, timestamp, received_signature, WEBHOOK_HMAC_KEY)
    
    if not is_valid:
        return False, 'Invalid signature'
    
    return True, 'Verified'

@app.route('/webhook-callback', methods=['POST'])
def handle_webhook():
    # 验证签名
    is_valid, message = verify_webhook_signature()
    
    if not is_valid:
        return jsonify({'error': message}), 401
    
    # 签名验证通过，处理回调数据
    data = request.json
    code = data.get('code')
    msg = data.get('msg')
    callback_data = data.get('data', {})
    task_id = callback_data.get('task_id')
    callback_type = callback_data.get('callbackType')
    
    print(f"收到合法的 Webhook 请求: {task_id}, 状态: {code}, 类型: {callback_type}")
    
    # 处理回调数据...
    
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```
</Tab>

<Tab title="PHP">
```php
<?php
header('Content-Type: application/json');

// 从环境变量或配置中读取 webhookHmacKey
$webhookHmacKey = getenv('WEBHOOK_HMAC_KEY');

function generateSignature($taskId, $timestampSeconds, $secret) {
    // 1. 拼接待签名字符串
    $dataToSign = $taskId . '.' . $timestampSeconds;
    
    // 2. 使用 HMAC-SHA256 计算签名
    $signature = hash_hmac('sha256', $dataToSign, $secret, true);
    
    // 3. Base64 编码
    return base64_encode($signature);
}

function verifySignature($taskId, $timestampSeconds, $receivedSignature, $secret) {
    // 重新生成签名
    $expectedSignature = generateSignature($taskId, $timestampSeconds, $secret);
    
    // 使用安全的字符串比较
    return hash_equals($expectedSignature, $receivedSignature);
}

function verifyWebhookSignature($webhookHmacKey) {
    // 1. 读取 Header 字段
    $timestamp = $_SERVER['HTTP_X_WEBHOOK_TIMESTAMP'] ?? null;
    $receivedSignature = $_SERVER['HTTP_X_WEBHOOK_SIGNATURE'] ?? null;
    
    if (!$timestamp || !$receivedSignature) {
        return ['valid' => false, 'error' => 'Missing signature headers'];
    }
    
    // 2. 验证签名
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $taskId = $data['data']['task_id'] ?? null;
    
    if (!$taskId) {
        return ['valid' => false, 'error' => 'Missing task_id'];
    }
    
    $isValid = verifySignature($taskId, $timestamp, $receivedSignature, $webhookHmacKey);
    
    if (!$isValid) {
        return ['valid' => false, 'error' => 'Invalid signature'];
    }
    
    return ['valid' => true, 'data' => $data];
}

// 验证签名
$result = verifyWebhookSignature($webhookHmacKey);

if (!$result['valid']) {
    http_response_code(401);
    echo json_encode(['error' => $result['error']]);
    exit;
}

// 签名验证通过，处理回调数据
$data = $result['data'];
$code = $data['code'] ?? null;
$msg = $data['msg'] ?? '';
$callbackData = $data['data'] ?? [];
$taskId = $callbackData['task_id'] ?? '';
$callbackType = $callbackData['callbackType'] ?? '';

error_log("收到合法的 Webhook 请求: $taskId, 状态: $code, 类型: $callbackType");

// 处理回调数据...

// 返回成功响应
http_response_code(200);
echo json_encode(['status' => 'received']);
?>
```
</Tab>

<Tab title="Java">
```java
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.Objects;

public class WebhookVerifier {
    
    public static boolean verifySignature(String taskId, long timestampSeconds, String receivedSignature, String secret) {
        // 重新生成签名
        String expectedSignature = generateSignature(taskId, timestampSeconds, secret);

        // 使用安全的字符串比较
        return constantTimeEquals(expectedSignature, receivedSignature);
    }

    public static String generateSignature(String taskId, long timestampSeconds, String secret) {
        try {
            // 1. 拼接待签名字符串
            String dataToSign = taskId + "." + timestampSeconds;

            // 2. 使用 HMAC-SHA256 计算签名
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec keySpec = new SecretKeySpec(
                    secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(keySpec);
            byte[] hash = mac.doFinal(dataToSign.getBytes(StandardCharsets.UTF_8));

            // 3. Base64 编码
            return Base64.getEncoder().encodeToString(hash);
        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("Failed to generate webhook signature", e);
        }
    }

    private static boolean constantTimeEquals(String a, String b) {
        if (a == null || b == null) {
            return Objects.equals(a, b);
        }
        if (a.length() != b.length()) {
            return false;
        }
        int result = 0;
        for (int i = 0; i < a.length(); i++) {
            result |= a.charAt(i) ^ b.charAt(i);
        }
        return result == 0;
    }
}
```
</Tab>
</Tabs>

### 示例 Webhook 请求

以下是一个完整的 webhook 请求示例：

```http
POST /your-webhook-endpoint HTTP/1.1
Host: your-server.com
Content-Type: application/json
X-Webhook-Timestamp: 1769670760
X-Webhook-Signature: KxDlpbbq0GDOKqm0+FuJpJWTzY8baHSjhEt4kwElqQI=

{
  "taskId": "ee9c2715375b7837f8bb51d641ff5863",
  "code": 200,
  "msg": "Success",
  "data": {
    "task_id": "ee9c2715375b7837f8bb51d641ff5863",
    "callbackType": "task_completed",
    ...
  }
}
```


