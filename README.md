## Description
A simple Flask demo.

## Detail

+ Jquery Ajax
+ Flask POST / GET / Templates

## Function

+ drama list
+ picture download
+ showroom-live hls url
+ program information

## API

### picdown

*Resource URL*

/v1/api/picdown

*Parameters*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| url | required | JSON | https://mdpr.jp/news/1727418 |

*Example Request*

GET https://yourdomain/v1/api/picdown?url=https://mdpr.jp/news/1727418

### drama

*Resource URL*

/v1/api/dramaget

*Parameters*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| id | required | JSON | tvbt / subpig / fixsub |

*Example Request*

GET https://yourdomain/v1/api/dramaget?id=tvbt

### program

*Resource URL*

/v1/api/programget

*Parameters*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| kw | required | JSON | nhk |

*Example Request*

GET https://yourdomain/v1/api/programget?kw=nhk
