import asyncio
import time

import httpx

lock = asyncio.Lock()

DEFAULT_MIN_INTERVAL = 30
OPERATION_API_TIMEOUT = 60


class ProxmoxClient:
    def __init__(self, logger, host, name, password):
        self._logger = logger
        self._host = host
        self._name = name
        self._password = password
        self._ticket = ""
        self._token = ""
        self._last_login = 0
        self._last_operation_time = 0
        self._last_status = ""

    async def login(self) -> bool:
        self._logger.info(f"login {self._host}")
        await lock.acquire()
        self._logger.info("get lock")
        try:
            if time.time() - self._last_login < DEFAULT_MIN_INTERVAL:
                return True
            login_url = f"{self._host}/api2/json/access/ticket"
            request_data = {"username": self._name, "password": self._password}
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.post(login_url, data=request_data)
            if res.status_code != 200:
                return False
            result = res.json()
            response_data = result["data"]
            self._token = response_data["CSRFPreventionToken"]
            self._ticket = response_data["ticket"]
            self._last_login = time.time()
            return True
        finally:
            lock.release()
            self._logger.info("release lock")

    async def shutdown_by_agent(self, node: str, vm_id: str) -> bool:
        try:
            self._logger.info(f"shutdown by agent, node: ({node}), vm: ({vm_id})")
            self._last_status = "stopping"
            self._last_operation_time = time.time()
            shutdown_url = (
                f"{self._host}/api2/json//nodes/{node}/qemu/{vm_id}/agent/shutdown"
            )
            headers = {"CSRFPreventionToken": self._token}
            cookies = {"PVEAuthCookie": self._ticket}
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.post(
                    shutdown_url,
                    headers=headers,
                    cookies=cookies,
                    timeout=OPERATION_API_TIMEOUT,
                )
            if res.status_code == 401:
                login_result = await self.login()
                if not login_result:
                    return False
                return await self.shutdown_by_agent(node, vm_id)
            return True
        except:
            self._logger.warning(
                f"shutdown machine error, node: ({node}), vm: ({vm_id}"
            )
            return False

    async def start(self, node: str, vm_id: str) -> bool:
        try:
            start_url = (
                f"{self._host}/api2/json//nodes/{node}/qemu/{vm_id}/status/start"
            )
            self._last_status = "running"
            self._last_operation_time = time.time()
            headers = {"CSRFPreventionToken": self._token}
            cookies = {"PVEAuthCookie": self._ticket}
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.post(
                    start_url,
                    headers=headers,
                    cookies=cookies,
                    timeout=OPERATION_API_TIMEOUT,
                )
            if res.status_code == 401:
                login_result = await self.login()
                if not login_result:
                    return False
                return await self.start(node, vm_id)
            return True
        except:
            self._logger.warning(f"start machine error, node: ({node}), vm: ({vm_id}")
            return False

    async def status(self, node: str, vm_id: str):
        try:
            self._logger.debug(f"get status, node: ({node}), vm: ({vm_id})")
            status_url = (
                f"{self._host}/api2/json//nodes/{node}/qemu/{vm_id}/status/current"
            )
            cookies = {"PVEAuthCookie": self._ticket}
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.get(status_url, cookies=cookies)
            if res.status_code == 401:
                login_result = await self.login()
                if not login_result:
                    return False
                return await self.status(node, vm_id)
            result = res.json()
            response_data = result["data"]
            status = response_data["status"]
            if time.time() - self._last_operation_time < DEFAULT_MIN_INTERVAL:
                if self._last_status == "stopping" and status == "running":
                    return "stopping"
                if self._last_status == "running" and status == "stopped":
                    return "running"
            self._last_status = status
            self._logger.debug(f"node: ({node}), vm: ({vm_id}), status: ({status})")
            return status
        except:
            self._logger.warning(
                f"get machine status error, node: ({node}), vm: ({vm_id}"
            )
            return False
