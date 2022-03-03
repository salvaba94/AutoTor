from autotor import TorRequests


class TorIP(TorRequests):
    """
    Example class to make requests and obtain the IPs used by Tor.
    """

    def request(
            self
        ) -> str:
        """
        This function makes a request to get the IP being used by Tor. 

        Returns
        -------
        ip : str
            IP being used by Tor.
        """
        ip_url = "http://httpbin.org/ip"
        session = self.get_tor_session()
        self.renew_tor_ip()
        ip = session.get(ip_url).json()["origin"]
        return ip