from fastapi import FastAPI

import SendNoti
import Watcher
import threading
import uvicorn
from pydantic import BaseModel

app = FastAPI()
watcher_thread = threading.Thread()


class Item(BaseModel):
    qrcodeurl: str
    deviceWashModelId: str
    washTemperatureId: str
    watching: bool = True
    time_interval: int = 5


@app.post('/createorder')
async def create_order_once(item: Item):
    result_code = Watcher.bookingWasher(qrcodeurl=str(item.qrcodeurl), deviceWashModelId=int(item.deviceWashModelId),
                                        washTemperatureId=int(item.washTemperatureId))
    if result_code == 1:
        return {'status': 1, 'message': '洗衣机预约成功，请在两分钟之内确定订单并付款！'}
    elif result_code == 0:
        return {'status': 0, 'message': '洗衣机现在被占用了！'}
    elif result_code == 3:
        return {'status': 3, 'message': '服务器返回了一个错误，我会将其发送到你的手机上！'}


@app.post('/watchingwasher')
async def watching_washer(item: Item):
    watching_thread = threading.Thread(target=Watcher.bookingWasher,
                                       args=(str(item.qrcodeurl), int(item.deviceWashModelId),
                                             int(item.washTemperatureId), item.watching,
                                             int(item.time_interval)))
    watching_thread.start()
    return '如果可用时将会发送通知到您的iPhone或Apple Watch上！'


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=39999)
