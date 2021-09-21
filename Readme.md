#  WasherWatcher使用指南及开发思路

##  使用指南

环境Python3.7 用fastapi作为后端，使用IFTTT作为手机端通知接收APP

clone本项目后，确保所有需要的库均已安装，然后修改config.py文件，Auth参数、geo参数均通过对U净APP抓包获取，在登录后抓取任意url为phoenix.ujing.online开头的数据包，在Headers中即可看到这两个参数。time_interval为监视洗衣机是否空闲的时间间隔，单位秒。IFTTT_url为在IFTTT应用中建立的webhook applet的url，通过对该url发送请求可以推送到手机端的IFTTT应用，实现通知的效果。

修改完config.py后，在服务器上运行main.py即可，可以在main.py中修改端口号。具体如何发送请求，请仔细阅读main.py代码。关键注意post的数据包字段要以JSON格式携带。

##  开发思路

首先需要获取洗衣机上的二维码，扫描后得到携带uuid的url，示例如下所示：

http:\/\/app.littleswan.com\/u_download.html?type=Ujing&uuid=0000000000000A0007604201907310020434

以此url作为JSON表单，请求scanWasherCode，如果返回deviceid，说明设备空闲，如果未返回，说明设备正在被使用，根据这一点来判断设备是否可以被预约

如果获取到了deviceid，则根据deviceid访问以下的url（假设deviceid为f11ef2dcb089ece93ced16b48ae4a670）

https://phoenix.ujing.online:443/api/v1/devices/f11ef2dcb089ece93ced16b48ae4a670

可以拿到这台device的所有参数，如类型、支持的洗涤方式、支持的温度等等，同时在返回的数据中，包含了store的信息，后续的请求需要store中的storeId，拿到storeId之后即可开始构建预约请求

发送预约请求通过以下url：

https://phoenix.ujing.online:443/api/v1/orders/create

使用POST方法，需要构建包含如下字段的JSON表单：

| 字段              | 说明                                                       |
| ----------------- | ---------------------------------------------------------- |
| deviceId          | 通过扫描二维码请求scanWasherCode得到的参数                 |
| deviceTypeId      | 表明设备类型，一般2为洗衣机，其他还有烘干机和洗鞋机等等    |
| storeId           | 通过携带deviceId请求得到的参数                             |
| washTemperatureId | 要预约订单的洗衣机温度，1为常温，2为30度，3为40度，4为60度 |
| type              | 默认为1，作用暂时未知                                      |
| deviceWashModelId | 洗涤模式，1为普通洗，2为小件洗，3为超强洗，4为单脱水       |

发送请求后，即预约成功，有两分钟的独占期(独占期内其他用户即使扫码也无法操作洗衣机)，并得到返回的订单ID，即orderId，可通过https://phoenix.ujing.online:443/api/v1/orders/{orderId}/detail?additional=price 查看预约的订单详情
