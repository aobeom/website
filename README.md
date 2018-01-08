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

POST https://yourdomain/v1/api/picdown

### drama

*Resource URL*

/v1/api/dramaget

*Parameters*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| id | required | JSON | tvbt / subpig / fixsub |

*Example Request*

POST https://yourdomain/v1/api/dramaget

### program

*Resource URL*

/v1/api/programget

*Parameters*

| Name | Required | Formats | Example |
|:-----:|:----:|:----:|:-----:|
| kw | required | JSON | a keyword |

*Example Request*

POST https://yourdomain/v1/api/programget
