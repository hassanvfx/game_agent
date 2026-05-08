# 通用 API 快速入门

> 用于账户管理和文件操作的基础实用 API

## 欢迎使用通用 API

通用 API 提供用于管理您的 kie.ai 账户和处理生成内容的基础实用服务。这些 API 能帮助您监控积分使用情况并高效地访问已生成的文件。

<CardGroup cols={2}>
  <Card title="查询账户积分" icon="lucide-wallet" href="/cn/common-api/get-account-credits">
    查看您当前的积分余额并监控使用情况
  </Card>

  <Card title="获取下载链接" icon="lucide-download" href="/cn/common-api/download-url">
    为已生成的文件生成临时下载链接
  </Card>
</CardGroup>

## 身份验证

所有 API 请求都需要使用 Bearer 令牌进行身份验证。请从 [API 密钥管理页面](https://kie.ai/api-key) 获取您的 API 密钥。

:::warning[]
请妥善保管您的 API 密钥，切勿公开分享。如果您怀疑密钥已泄露，请立即重置。
:::

### API 基础 URL (Base URL)

```
https://api.kie.ai
```

### 认证 Header

```http
Authorization: Bearer YOUR_API_KEY
```

## 快速入门指南

### 第一步：检查积分余额

监控您的账户积分，以确保有足够的余额持续使用服务：

<Tabs>
  <TabItem value="cURL" label="cURL">
    ```bash
    curl -X GET "https://api.kie.ai/api/v1/chat/credit" \
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
  </TabItem>

  <TabItem value="JavaScript" label="JavaScript">
    ```javascript
    const response = await fetch('https://api.kie.ai/api/v1/chat/credit', {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer YOUR_API_KEY'
      }
    });

    const result = await response.json();
    console.log('Current credits:', result.data);
    ```
  </TabItem>

  <TabItem value="Python" label="Python">
    ```python
    import requests

    url = "https://api.kie.ai/api/v1/chat/credit"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    print(f"Current credits: {result['data']}")
    ```
  </TabItem>
</Tabs>

**响应示例：**

```json
{
  "code": 200,
  "msg": "success",
  "data": 100
}
```

### 第二步：获取生成文件的下载链接

将生成文件的 URL 转换为临时的可下载链接：

<Tabs>
  <TabItem value="cURL" label="cURL">
    ```bash
    curl -X POST "https://api.kie.ai/api/v1/common/download-url" \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "url": "https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98"
      }'
    ```
  </TabItem>

  <TabItem value="JavaScript" label="JavaScript">
    ```javascript
    const response = await fetch('https://api.kie.ai/api/v1/common/download-url', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: 'https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98'
      })
    });

    const result = await response.json();
    console.log('Download URL:', result.data);
    ```
  </TabItem>

  <TabItem value="Python" label="Python">
    ```python
    import requests

    url = "https://api.kie.ai/api/v1/common/download-url"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }

    payload = {
        "url": "https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98"
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    print(f"Download URL: {result['data']}")
    ```
  </TabItem>
</Tabs>

**响应示例：**

```json
{
  "code": 200,
  "msg": "success",
  "data": "https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98"
}
```

:::warning[]
下载链接有效期**仅为 20 分钟**。请确保在此时间内下载或缓存内容。
:::

## API 概览

### 查询账户积分

<Card title="GET /api/v1/chat/credit" icon="lucide-wallet">
  **用途**：监控您的账户积分余额

  **特性**：

  * 实时获取积分余额
  * 无需任何参数
  * 即时响应
  * 监控使用情况必不可少

  **使用场景**：

  * 在开始生成任务前检查积分
  * 监控积分消耗模式
  * 规划积分充值
  * 实现积分阈值预警
</Card>

### 获取下载链接

<Card title="POST /api/v1/common/download-url" icon="lucide-download">
  **用途**：为已生成的文件生成临时下载链接

  **特性**：

  * 支持所有 kie.ai 生成的文件类型（图像、视频、音频等）
  * 20 分钟有效期
  * 安全的认证访问
  * 仅适用于 kie.ai 生成的 URL

  **使用场景**：

  * 下载生成内容到本地存储
  * 与团队成员分享临时链接
  * 集成到外部系统
  * 构建自定义下载工作流
</Card>

## 实战示例

### 积分监控系统

实现一个自动化的积分监控系统：

<Tabs>
  <TabItem value="JavaScript" label="JavaScript">
    ```javascript
    class KieAIClient {
      constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.kie.ai';
      }
      
      async getCredits() {
        const response = await fetch(`${this.baseUrl}/api/v1/chat/credit`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to get credits: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data;
      }
      
      async getDownloadUrl(fileUrl) {
        const response = await fetch(`${this.baseUrl}/api/v1/common/download-url`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url: fileUrl })
        });
        
        if (!response.ok) {
          throw new Error(`Failed to get download URL: ${response.statusText}`);
        }
        
        const result = await response.json();
        return result.data;
      }
      
      async downloadFile(fileUrl, outputPath) {
        // 获取下载链接
        const downloadUrl = await this.getDownloadUrl(fileUrl);
        
        // 下载文件
        const response = await fetch(downloadUrl);
        const buffer = await response.arrayBuffer();
        
        // 保存到文件 (Node.js)
        const fs = require('fs');
        fs.writeFileSync(outputPath, Buffer.from(buffer));
        
        console.log(`File downloaded to: ${outputPath}`);
      }
      
      async checkCreditsAndWarn(threshold = 10) {
        const credits = await this.getCredits();
        
        if (credits < threshold) {
          console.warn(`⚠️  Low credits warning: ${credits} credits remaining`);
          return false;
        }
        
        console.log(`✓ Credits available: ${credits}`);
        return true;
      }
    }

    // 使用示例
    const client = new KieAIClient('YOUR_API_KEY');

    // 操作前监控积分
    async function runWithCreditCheck() {
      const hasEnoughCredits = await client.checkCreditsAndWarn(20);
      
      if (!hasEnoughCredits) {
        console.error('Insufficient credits. Please recharge your account.');
        return;
      }
      
      // 积分验证通过，继续执行操作
      console.log('Credits verified. Proceeding with operations...');
    }

    // 下载生成的文件
    async function downloadGeneratedFiles(fileUrls) {
      for (let i = 0; i < fileUrls.length; i++) {
        try {
          await client.downloadFile(
            fileUrls[i],
            `./downloads/file-${i + 1}.mp4`
          );
          console.log(`✓ Downloaded file ${i + 1}/${fileUrls.length}`);
        } catch (error) {
          console.error(`✗ Failed to download file ${i + 1}:`, error.message);
        }
      }
    }

    // 定期积分监控
    async function monitorCredits(intervalMinutes = 60) {
      setInterval(async () => {
        try {
          const credits = await client.getCredits();
          console.log(`[${new Date().toISOString()}] Current credits: ${credits}`);
          
          if (credits < 50) {
            // 发送警报 (邮件, webhook 等)
            console.warn('ALERT: Credits below 50!');
          }
        } catch (error) {
          console.error('Credit check failed:', error.message);
        }
      }, intervalMinutes * 60 * 1000);
    }
    ```
  </TabItem>

  <TabItem value="Python" label="Python">
    ```python
    import requests
    import time
    import os
    from datetime import datetime
    from typing import Optional

    class KieAIClient:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.base_url = 'https://api.kie.ai'
            self.headers = {
                'Authorization': f'Bearer {api_key}'
            }
        
        def get_credits(self) -> int:
            """获取当前账户积分"""
            response = requests.get(
                f'{self.base_url}/api/v1/chat/credit',
                headers=self.headers
            )
            
            if not response.ok:
                raise Exception(f'Failed to get credits: {response.text}')
            
            result = response.json()
            return result['data']
        
        def get_download_url(self, file_url: str) -> str:
            """获取生成文件的临时下载链接"""
            response = requests.post(
                f'{self.base_url}/api/v1/common/download-url',
                headers={**self.headers, 'Content-Type': 'application/json'},
                json={'url': file_url}
            )
            
            if not response.ok:
                raise Exception(f'Failed to get download URL: {response.text}')
            
            result = response.json()
            return result['data']
        
        def download_file(self, file_url: str, output_path: str) -> None:
            """从 kie.ai URL 下载文件"""
            # 获取下载链接
            download_url = self.get_download_url(file_url)
            
            # 下载文件
            response = requests.get(download_url)
            
            if not response.ok:
                raise Exception(f'Failed to download file: {response.text}')
            
            # 保存到文件
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f'File downloaded to: {output_path}')
        
        def check_credits_and_warn(self, threshold: int = 10) -> bool:
            """检查积分，如果低于阈值则发出警告"""
            credits = self.get_credits()
            
            if credits < threshold:
                print(f'⚠️  Low credits warning: {credits} credits remaining')
                return False
            
            print(f'✓ Credits available: {credits}')
            return True

    # 使用示例
    def main():
        client = KieAIClient('YOUR_API_KEY')
        
        # 操作前监控积分
        def run_with_credit_check():
            has_enough_credits = client.check_credits_and_warn(threshold=20)
            
            if not has_enough_credits:
                print('Insufficient credits. Please recharge your account.')
                return
            
            print('Credits verified. Proceeding with operations...')
        
        # 下载生成的文件
        def download_generated_files(file_urls: list):
            for i, file_url in enumerate(file_urls):
                try:
                    client.download_file(
                        file_url,
                        f'./downloads/file-{i + 1}.mp4'
                    )
                    print(f'✓ Downloaded file {i + 1}/{len(file_urls)}')
                except Exception as e:
                    print(f'✗ Failed to download file {i + 1}: {e}')
        
        # 定期积分监控
        def monitor_credits(interval_minutes: int = 60):
            while True:
                try:
                    credits = client.get_credits()
                    timestamp = datetime.now().isoformat()
                    print(f'[{timestamp}] Current credits: {credits}')
                    
                    if credits < 50:
                        # 发送警报 (邮件, webhook 等)
                        print('ALERT: Credits below 50!')
                except Exception as e:
                    print(f'Credit check failed: {e}')
                
                time.sleep(interval_minutes * 60)
        
        # 示例执行
        print('Checking credits...')
        run_with_credit_check()
        
        print('\nDownloading files...')
        file_urls = [
            'https://tempfile.1f6cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbd98',
            'https://tempfile.2f7dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxcd99'
        ]
        download_generated_files(file_urls)

    if __name__ == '__main__':
        main()
    ```
  </TabItem>
</Tabs>

## 错误处理

常见错误及处理方法：

<details>
  <summary>401 Unauthorized (未授权)</summary>
  
  ```javascript
  // 检查 API 密钥是否正确
  if (response.status === 401) {
    console.error('Invalid API key, please check Authorization header');
    // 重新获取或更新 API 密钥
  }
  ```
</details>

<details>
  <summary>422 Validation Error (验证错误 - 下载链接)</summary>

  ```javascript
  // 仅支持 kie.ai 生成的 URL
  if (response.status === 422) {
    const error = await response.json();
    console.error('Invalid URL:', error.msg);
    // 确保您使用的是 kie.ai 生成的文件 URL
    // 不支持外部 URL
  }
  ```
</details>

<details>
  <summary>402 Insufficient Credits (积分不足)</summary>

  ```javascript
  // 积分耗尽，需要充值
  if (response.status === 402) {
    console.error('Insufficient credits. Please recharge your account.');
    // 重定向到积分购买页面
    // 或向管理员发送通知
  }
  ```
</details>

<details>
  <summary>500 Server Error (服务器错误)</summary>

  ```javascript
  // 实现重试机制
  async function apiCallWithRetry(apiFunction, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await apiFunction();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        
        // 指数退避 (Exponential backoff)
        const delay = Math.pow(2, i) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  ```
</details>

## 最佳实践

<details>
  <summary>积分管理</summary>
  * **定期监控**：在开始大批量操作前检查积分
  * **设置预警**：当积分低于阈值时，实施自动化报警
  * **预算规划**：追踪积分消耗模式以便更好地进行规划
  * **优雅降级**：适当处理积分不足的情况
</details>

<details>
  <summary>下载链接使用</summary>
  * **时效性**：下载链接在 20 分钟后过期
  * **适当缓存**：获取下载链接后立即保存文件
  * **批量下载**：在时限内高效处理多个文件
  * **错误处理**：为失败的下载实施重试逻辑
</details>

<details>
  <summary>性能优化</summary>
  * **并行处理**：并发下载多个文件（需遵守速率限制）
  * **连接池**：复用 HTTP 连接进行多次请求
  * **超时设置**：为下载操作设置合理的超时时间
  * **进度追踪**：为长时间运行的操作实现进度指示
</details>

<details>
  <summary>安全考量</summary>
  * **API 密钥保护**：切勿在客户端代码中暴露 API 密钥
  * **仅限 HTTPS**：始终使用 HTTPS 进行 API 请求
  * **密钥轮换**：定期轮换 API 密钥以确保安全
  * **访问日志**：保留 API 使用日志以供审计
</details>

## 重要提示

:::warning[]
**下载链接过期**：临时下载链接有效期**仅为 20 分钟**。请确保：

* 获取 URL 后立即下载文件
* 实现过期 URL 的错误处理
* 缓存下载内容以供将来使用
:::

:::info[]
**积分余额**：当积分耗尽时，服务访问将受限。请务必：

* 定期监控积分余额
* 设置低积分预警
* 提前规划积分充值
* 在积分较低时实现优雅降级
:::

:::note[]
**支持的 URL**：下载链接端点仅支持由 kie.ai 服务生成的文件。外部文件 URL 将导致 422 验证错误。
:::
    
## 集成示例

<CardGroup cols={2}>
  <Card title="市场 API" icon="lucide-store" href="/cn/market/quickstart">
    探索 AI 模型市场 API
  </Card>

  <Card title="文件上传 API" icon="lucide-upload" href="/cn/file-upload-api/quickstart">
    上传文件以进行处理
  </Card>
</CardGroup>

## 技术支持

:::info[]
需要帮助？我们的技术支持团队随时为您服务。

* **电子邮箱**: [support@kie.ai](mailto:support@kie.ai)
* **文档**: [docs.kie.ai](https://docs.kie.ai)
* **API 状态**: 查看我们的状态页面以获取实时 API 健康状况
:::

***

准备好开始了吗？[获取您的 API 密钥](https://kie.ai/api-key) 并立即开始使用通用 API 服务！
