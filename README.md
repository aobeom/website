## 简介
一个基于Flask的简单的且不太严谨的伪RESTful API应用


## 主要功能

+ 提取[新闻网站](https://github.com/aobeom/picdown)的原图地址和HLS直播地址
+ 剧的资源链接
+ 雅虎电视节目搜索结果的美化
+ 17杂APP的视频区
+ 简单认证接口

## API说明

### 1 获取新闻图片或直播地址

*请求URL*

GET /api/v1/media/news  
GET /api/v1/media/hls

*请求参数*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| url | required | JSON | https://mdpr.jp/news/1727418 |

*请求示例*

GET https://yourdomain/api/v1/media/news?url=https://mdpr.jp/news/1727418

### 2-1 获取剧的资源地址

*请求URL*

GET /api/v1/drama

*请求参数*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| / | required | JSON | tvbt / subpig / fixsub |

*请求示例*

GET https://yourdomain/api/v1/drama/tvbt

### 2-2 获取剧列表的更新时间

*请求URL*

GET /api/v1/drama/time

### 3 搜索结果的美化

*请求URL*

GET /api/v1/program

*请求参数*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| kw | required | JSON | nhk |
| ac | required | JSON | 23 |

**ac是区域代码，23代表东京**

*请求示例*

GET https://yourdomain/api/v1/program?kw=nhk&ac=23

### 4 17杂视频

*请求URL*

GET /api/v1/stchannel

**仅为最终内容列表，暂无原始数据接口和视频下载接口**

### 5 渡边梨加message

*请求URL*

GET /api/v1/rikamsg

*请求参数*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| type | Required | JSON | 0, 1, 2, 3, 100 |
| page | Options | JSON | Number |

+ 0 纯文本
+ 1 只包含图片
+ 2 只包含视频
+ 3 只包含音频
+ 100 所有内容

**仅为最终内容列表**

*请求示例*

#### 获取所有内容的总页数
GET https://yourdomain/api/v1/rikamsg?type=100  
#### 获取所有内容的第一页
GET https://yourdomain/api/v1/rikamsg?type=100&page=1

### 6. 注册/登录/登出

*请求URL*

POST /api/v1/register  
POST /api/v1/login  
POST /api/v1/logout

*请求参数*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| username | Required | JSON | / |
| password | Required | JSON | / |

*请求示例*

POST https://yourdomain/api/v1/register  
POST https://yourdomain/api/v1/login  
POST https://yourdomain/api/v1/logout  

## 速率限制

默认每个IP地址10秒内连续请求不能超过10次