from typing import Any, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from writers.base import IWriter



RETRIES: int = 3
BACKOFF_FACTOR: float = 0.3




class HttpWriter(IWriter):

    def __init__(self, destination, machine_id:int,  timeout: float = 10.0) -> None:
        super().__init__(destination, machine_id)

        self.__timeout = timeout

        self.session = requests.Session()

        status_forcelist = (429, 500, 502, 503, 504)
        retry = Retry(
            total=RETRIES,
            read=RETRIES,
            connect=RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=status_forcelist,
            allowed_methods={"POST"},
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)


    def send_data(self, data: Dict[str, Any]) -> int:
        req_headers = {"X-Machine-id": self._machine_id}
        try:
            resp = self.session.post(
                self._destination,
                json=data,
                headers=req_headers,
                timeout=self.__timeout,
            )
            return resp.status_code
        except requests.exceptions.RequestException as e:
            print(e)
            return None


