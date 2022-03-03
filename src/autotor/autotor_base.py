import requests
from requests import Session
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from stem.process import launch_tor_with_config
from typing import Type, Optional
from types import TracebackType 
import abc
import time
import urllib
import zipfile
from pathlib import Path
import subprocess
import re
import string
import random



class TorRequests(abc.ABC):
    """
    Base class to implement functionality for web scraping through Tor from 
    Windows.
    """

    def __init__(
            self,
            tor_link: Optional[str] = 
                "https://www.torproject.org/dist/torbrowser/11.0.6/tor-win32-0.4.6.9.zip",
            tor_root: Optional[str] = ".."
        ) -> None:
        """
        Member function to initialise the class configuration and download Tor.
        
        Parameters
        ----------
        tor_link : str
            Link from which to download Tor Windows Expert Bundle. Default is 
            "https://www.torproject.org/dist/torbrowser/11.0.6/tor-win32-0.4.6.9.zip".
        tor_root : str
            Tor root path. Default is "..".

        Returns
        -------
        None : NoneType
            No return.
        """

        cwd = Path.cwd()
        self.__config = {
            "TOR_LINK": tor_link,
            "TOR_DIR": cwd.joinpath(tor_root, "TorBrowser"),
            "TOR_CMD": cwd.joinpath(tor_root, "TorBrowser", "Tor", "tor.exe"),
            "LOCALHOST": "127.0.0.1",
            "SOCK_TOR_PORT": 9050,
            "CONT_TOR_PORT": 9051,
            "PASSWORD": None
        }

        self.__dowload_tor()


    def __enter__(
            self
        ):
        """
        Sequence of operations to execute each time the context manager is 
        entered. The function initiates a Tor process in a control port and 
        with authentication. 
        
        Parameters
        ----------
        self : TorRequests
            This object.

        Returns
        -------
        self : TorRequests
            This object.
        """
        self.__config["PASSWORD"] = self.__random_password(random.randint(10, 20))
        hash_password = self.__generate_tor_hash()
        
        launch_config = {
                "ControlPort": str(self.__config["CONT_TOR_PORT"]),
                "HashedControlPassword": str(hash_password),
                "CookieAuthentication": "1"
            }

        self.tor = launch_tor_with_config(
            config = launch_config,
            tor_cmd = str(self.__config["TOR_CMD"]))

        return self


    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]] = None, 
            exc_value: Optional[BaseException] = None,
            traceback: Optional[TracebackType] = None
        ) -> None:
        """
        Sequence of operations to execute each time the context manager is 
        exited. The function kills the Tor process.

        Parameters
        ----------
        exc_type : Type(BaseException)
            Exception type. Default is None.
        exc_value : BaseException
            Exception value. Default is None.
        traceback : TracebackType
            Traceback. Default is None.

        Returns
        -------
        None : NoneType
            No return.
        """
        self.tor.kill()
        self.__config["PASSWORD"] = None


    def __dowload_tor(
            self
        ) -> None:
        """ 
        This function downloads Tor if not already downloaded.
        
        Parameters
        ----------
        self : TorRequests
            This object.

        Returns
        -------
        None : NoneType
            No return.
        """
        self.__config["TOR_DIR"].mkdir(parents = True, exist_ok = True)

        if not self.__config["TOR_DIR"].joinpath("Tor").is_dir():
            zip_path, _ = urllib.request.urlretrieve(self.__config["TOR_LINK"])
            with zipfile.ZipFile(zip_path, "r") as file:
                file.extractall(self.__config["TOR_DIR"])


    def __random_password(
            self,
            length: int
        ) -> str:
        """
        Member function to generate a random password containing digits, 
        ASCII letters and punctuation.

        Parameters
        ----------
        self : TorRequests
            This object.
        length : int
            Integer length of the password.
    
        Returns
        -------
        password : str
            String containing the randomly generated password.
        """
        letters = string.punctuation + string.digits + string.ascii_letters
        password = "".join([random.choice(letters) for i in range(length)])
        return password


    def __generate_tor_hash(
            self,
        ) -> str:
            
        """ 
        Member fucntion to launch a Tor subprocess to generate a hashed password.

        Parameters
        ----------
        self : TorRequests
            This object.

        Returns
        -------
        hashed_password : str
            String containing the hashed password.
        """
        process = subprocess.Popen([str(self.__config["TOR_CMD"]), 
                                    "--hash-password", self.__config["PASSWORD"]], 
                                    stdout = subprocess.PIPE)
        stdout, _ = process.communicate()
        
        match = re.search(r"(\\r\\n16:.{58})", str(stdout))
        hashed_password = re.sub(r"(\\r\\n)", "", match.group(0))
        return hashed_password


    def renew_tor_ip(
            self
        ) -> None:
        """
        Member function that renews the Tor circuit (to get another IP) by 
        sending a NEWNYM signal and waiting for a prudent time.

        Parameters
        ----------
        self : TorRequests
            This object.

        Returns
        -------
        None : NoneType
            No return.
        """
        with Controller.from_port(port = self.__config["CONT_TOR_PORT"]) as controller:
            controller.authenticate(password = self.__config["PASSWORD"])
            controller.signal(Signal.NEWNYM)
            time.sleep(controller.get_newnym_wait())


    def get_tor_session(
            self
        ) -> Session:
        """
        This member function gets a Tor session.

        Parameters
        ----------
        self : TorRequests
            This object.

        Returns
        -------
        session : Session
            Session object connected to Tor.
        """
        
        session = requests.session()
        proxy = "socks5://" + self.__config["LOCALHOST"] + ":" + str(
            self.__config["SOCK_TOR_PORT"])

        session.proxies = {"http": proxy, "https": proxy}
        session.headers = {"User-Agent": UserAgent().random}
        return session


    @abc.abstractmethod
    def request(
            self
        ) -> None:
        """
        This member function is thought of to be overrided upon inheritance.

        Parameters
        ----------
        self : TorRequests
            This object.
            
        Returns
        -------
        None : NoneType
            No return.
        """
        pass
