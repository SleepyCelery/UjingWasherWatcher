import requests
import time
import SendNoti
from config import *
from url import *

headers = {
    'Host': 'phoenix.ujing.online:443',
    'Authorization': Auth,
    'x-user-geo': geo,
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-Hans-CN;q=1',
    'Accept': '*/*',
    'User-Agent': 'iPhone13,1(iOS/14.8) AliApp(WeexDemo/1.0.0) Weex/0.28.0 1125x2436',
    'Connection': 'keep-alive',
}

idle_flag = bool()


def tprint(string: str):
    print('[{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string))


def get_deviceId(qrcodeurl):
    json_payload = {
        'qrCode': qrcodeurl
    }
    response = requests.post(url=scancode_url, json=json_payload, headers=headers)
    result = response.json()['data']['result']
    if 'deviceId' in result.keys():
        return result['deviceId']
    return None


def get_storeId(deviceId):
    info_dict = {}
    response = requests.get(url=deviceinfo_url.format(deviceId=deviceId), headers=headers)

    storeinfo = response.json()
    # print(storeinfo)
    if 'storeId' in storeinfo['data']['store'].keys():
        info_dict['storeId'] = storeinfo['data']['store']['storeId']

    if 'type' in storeinfo['data'].keys():
        info_dict['type'] = storeinfo['data']['type']

    if 'deviceTypeId' in storeinfo['data']['device'].keys():
        info_dict['deviceTypeId'] = storeinfo['data']['device']['deviceTypeId']

    return info_dict


def createOrder(deviceId, storeId, deviceTypeId, type, deviceWashModelId, washTemperatureId):
    '''
    :param deviceId: 通过扫描二维码请求scanWasherCode得到的参数
    :param storeId: 通过携带deviceId请求得到的参数
    :param deviceTypeId: 表明设备类型，一般2为洗衣机，其他还有烘干机和洗鞋机等等
    :param type: 默认为1，作用暂时未知
    :param deviceWashModelId: 洗涤模式，1为普通洗，2为小件洗，3为超强洗，4为单脱水
    :param washTemperatureId: 要预约订单的洗衣机温度，1为常温，2为30度，3为40度，4为60度
    :return: 服务器返回信息
    '''
    json_payload = {
        'deviceId': deviceId,
        'deviceTypeId': deviceTypeId,
        'storeId': storeId,
        'washTemperatureId': washTemperatureId,
        'type': type,
        'deviceWashModelId': deviceWashModelId
    }
    response = requests.post(url=ordercreate_url, headers=headers, json=json_payload)
    info = response.json()
    if 'orderId' not in info['data'].keys():
        return False
    return True


def bookingWasher(qrcodeurl: str, deviceWashModelId: int, washTemperatureId: int, watching=False,
                  time_interval=5) -> int:
    '''
    :param qrcodeurl: 洗衣机上的二维码对应的url
    :param deviceWashModelId: 洗涤模式，1为普通洗，2为小件洗，3为超强洗，4为单脱水
    :param washTemperatureId: 要预约订单的洗衣机温度，1为常温，2为30度，3为40度，4为60度
    :param watching: 是否监视洗衣机，True表示监视，即在洗衣机被占用时隔time_interval秒后再次请求预约，False表示不监视，适用于一次性获取洗衣机状态
    :return: 返回1为单次预约成功，返回3为运行时遇到错误，返回2为监视状态下预约成功,返回0为单次预约失败
    '''
    try:
        deviceId = get_deviceId(qrcodeurl)
        info = get_storeId(deviceId)
        if watching:
            while not createOrder(deviceId=deviceId, deviceTypeId=info['deviceTypeId'], storeId=info['storeId'],
                                  type=info['type'],
                                  washTemperatureId=washTemperatureId, deviceWashModelId=deviceWashModelId):
                time.sleep(time_interval)
            SendNoti.SendNotification('洗衣机预约成功，请在两分钟之内确定订单并付款！')
            return 2
        else:
            if createOrder(deviceId=deviceId, deviceTypeId=info['deviceTypeId'], storeId=info['storeId'],
                           type=info['type'],
                           washTemperatureId=washTemperatureId, deviceWashModelId=deviceWashModelId):
                return 1
            else:
                return 0
    except Exception as e:
        SendNoti.SendNotification('运行时遇到错误：{}'.format(e))
        return 3
