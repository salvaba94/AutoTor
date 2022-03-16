from autotor import TorRequests
from typing import List
from threading import Lock


GLOBAL_LOCK = Lock()


class TorIP(TorRequests):
    """
    Example class to make requests and obtain the IPs used by Tor.
    """

    def __init__(
            self, 
            *args, 
            **kwargs
        ) -> None:
        """
        This function initialises the class with the URL to which the requests 
        will be made to .
        """

        super(TorIP, self).__init__(*args, **kwargs)

        self.ip_url = "http://httpbin.org/ip"


    def request(
            self,
            elem: List[int],
            n_id: int
        ) -> List[str]:
        """
        This function makes a request to get the IP being used by Tor from a 
        specific thread. It makes as many requests as configured in the 
        initialisation.

        Parameters
        ----------
        elem : List[int]
            List requests to make in current thread. Passed by threaded_request 
            in batches.
        n_id : int
            Thread ID.

        Returns
        -------
        ips : List[str]
            List of retrieved IPs.
        """

        fmt = "{:10s} | {:15s} | {:10s}"

        with GLOBAL_LOCK:
            if n_id == 0:
                log_col = ["Thread", "Tor IP", "Response"]
                print(fmt.format(*log_col))
                print("-" * (15 + (10 + 3) * 2))
        
        ips = []
        for _ in range(len(elem)):

            success = False
            while not success:

                session = self.get_tor_session(n_id)
                self.renew_tor_ip(n_id)

                response = session.get(self.ip_url)

                if response.status_code == 200:
                    success = True
                else:
                    continue

                ip = response.json()["origin"]

                with GLOBAL_LOCK:
                    log_data = [str(n_id)] + [ip] + [str(response.status_code)]
                    print(fmt.format(*log_data))

                ips.append(ip)

        return ips