import requests
import time
import urllib
import zipfile

import re
import string
import random
import socket
import shutil
import numpy as np


from subprocess import Popen, PIPE
from requests import Session
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from stem.process import launch_tor_with_config
from typing import Type, Optional, List, Any
from types import TracebackType 
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod
from pathlib import Path



class TorRequests(ABC):
    """
    Base class to implement functionality for parallel requesting through Tor 
    from Windows.
    """

    def __init__(
            self,
            tor_link: Optional[str] = 
                "https://www.torproject.org/dist/torbrowser/11.0.6/tor-win32-0.4.6.9.zip",
            tor_root: Optional[str] = "..",
            n_process: Optional[int] = 1
        ) -> None:
        """
        Member function to initialise the class configuration and download Tor.
        
        Parameters
        ----------
        tor_link : str, optional
            Link from which to download Tor Windows Expert Bundle. Default is 
            "https://www.torproject.org/dist/torbrowser/11.0.6/tor-win32-0.4.6.9.zip".
        tor_root : str, optional
            Tor root path. Default is "..".
        n_process : int, optional
            Number of Tor processes and Python threads to launch in parallel. 
            Default is 1.
        """

        cwd = Path.cwd()

        self.__config = {
            "TOR_LINK": tor_link,
            "TOR_DIR": cwd.joinpath(tor_root, "TorBrowser"),
            "TOR_CMD": cwd.joinpath(tor_root, "TorBrowser", "Tor", "tor.exe"),
            "N_PROCESS": n_process,
            "LOCALHOST": "127.0.0.1",
            "DATA_DIR": None,
            "SOCKS_TOR_PORT": None,
            "CONTROL_TOR_PORT": None,
            "PASSWORD": None,
            "HASH_PASSWORD": None
        }

        self.__dowload_tor()
        

    def __enter__(
            self
        ) -> "TorRequests":
        """
        Sequence of operations to execute each time the context manager is 
        entered. The function initiates all Tor processes in parallel.
        """

        self.executor = ThreadPoolExecutor(max_workers = self.__config["N_PROCESS"])
        self.__populate_config()
        
        
        futures = [self.executor.submit(self.__launch_tor, n_id = n_id) 
                   for n_id in range(self.__config["N_PROCESS"])]
        self.tor = [future.result() for future in as_completed(futures)]

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
        exc_type : Type(BaseException), Optional
            Exception type. Default is None.
        exc_value : BaseException, Optional
            Exception value. Default is None.
        traceback : TracebackType, Optional
            Traceback. Default is None.
        """

        for tor in self.tor:
            tor.kill()
        
        self.executor.shutdown()
        
        for path in self.__config["DATA_DIR"]:
            shutil.rmtree(path)

        self.__config["PASSWORD"] = None
        self.__config["HASH_PASSWORD"] = None            
        self.__config["SOCKS_TOR_PORT"] = None
        self.__config["CONTROL_TOR_PORT"] = None
        self.__config["DATA_DIR"] = None


    def __dowload_tor(
            self
        ) -> None:
        """ 
        This function downloads Tor if not already downloaded.
        """

        self.__config["TOR_DIR"].mkdir(parents = True, exist_ok = True)

        if not self.__config["TOR_DIR"].joinpath("Tor").is_dir():
            zip_path, _ = urllib.request.urlretrieve(self.__config["TOR_LINK"])
            with zipfile.ZipFile(zip_path, "r") as file:
                file.extractall(self.__config["TOR_DIR"])
                

    def __launch_tor(
            self,
            n_id: int
        ) -> Popen:
        """
        Member function to that launches Tor processes with specific 
        configurations depending on the thread.

        Parameters
        ----------
        n_id : int
            Thread ID needed to access the corresponding configuration.
    
        Returns
        -------
        tor : Popen
            Tor process handle.
        """

        launch_config = {
            "SOCKSPort": str(self.__config["SOCKS_TOR_PORT"][n_id]),
            "DataDir": str(self.__config["DATA_DIR"][n_id]),
            "ControlPort": str(self.__config["CONTROL_TOR_PORT"][n_id]),
            "HashedControlPassword": self.__config["HASH_PASSWORD"][n_id],
            "CookieAuthentication": "1"
        }
            
        tor = launch_tor_with_config(
                config = launch_config,
                tor_cmd = str(self.__config["TOR_CMD"]))

        return tor


    def __populate_config(
            self
        ) -> None:
        """
        This function populates the thread-dependent part of the configuration 
        of the class. It includes Tor socks and control ports (taking free ports
        from the system), normal and hashed control passwords, and data directories.
        """

        socks = []
        for _ in range(2 * self.__config["N_PROCESS"]):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.__config["LOCALHOST"], 0))
            socks.append(sock)

        ports = []
        for sock in socks:
            _, port = sock.getsockname()
            ports.append(port)
            sock.close()

        ports = np.array(ports).reshape((2, -1), order = "F")
        self.__config["SOCKS_TOR_PORT"] = ports[0, :]
        self.__config["CONTROL_TOR_PORT"] = ports[-1, :]

        self.__config["PASSWORD"] = [self.__random_password(random.randint(10, 20)) 
            for _ in range(self.__config["N_PROCESS"])]
        self.__config["HASH_PASSWORD"] = [self.__generate_tor_hash(password) 
            for password in self.__config["PASSWORD"]]
        
        self.__config["DATA_DIR"] = []
        for n_id in range(self.__config["N_PROCESS"]):
            data_dir = self.__config["TOR_DIR"].joinpath("Data" + str(n_id))
            data_dir.mkdir(parents = True, exist_ok = True)
            self.__config["DATA_DIR"].append(data_dir)


    def __random_password(
            self,
            length: int
        ) -> str:
        """
        Member function to generate a random password containing digits, 
        ASCII letters and punctuation.

        Parameters
        ----------
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
            password: str
        ) -> str:
            
        """ 
        Member fucntion to launch a Tor subprocess to generate a hashed password.

        Parameters
        ----------
        password : str
            String containing the password.

        Returns
        -------
        hashed_password : str
            String containing the hashed password.
        """

        process = Popen([str(self.__config["TOR_CMD"]), "--hash-password", password], 
                        stdout = PIPE)
        stdout, _ = process.communicate()
        
        match = re.search(r"(\\r\\n16:.{58})", str(stdout))
        hashed_password = re.sub(r"(\\r\\n)", "", match.group(0))
        return hashed_password


    def renew_tor_ip(
            self,
            n_id: int
        ) -> None:
        """
        Member function that renews the Tor circuit (to get another IP) by 
        sending a NEWNYM signal and waiting for a prudent time.

        Parameters
        ----------
        n_id : int
            Thread ID needed to access the corresponding configuration.
        """

        with Controller.from_port(port = self.__config["CONTROL_TOR_PORT"][n_id]) \
            as controller:
            controller.authenticate(password = self.__config["PASSWORD"][n_id])
            controller.signal(Signal.NEWNYM)
            time.sleep(controller.get_newnym_wait())


    def get_tor_session(
            self,
            n_id
        ) -> Session:
        """
        This member function gets a Tor session.

        Parameters
        ----------
        n_id : int
            Thread ID needed to access the corresponding configuration.

        Returns
        -------
        session : Session
            Session object connected to Tor.
        """
        
        session = requests.session()
        proxy = "socks5://" + self.__config["LOCALHOST"] + ":" + str(
            self.__config["SOCKS_TOR_PORT"][n_id])

        session.proxies = {"http": proxy, "https": proxy}
        session.headers = {"User-Agent": UserAgent().random}
        return session


    def threaded_request(
            self,
            elements: List[Any]
        ) -> List[Any]:
        """
        This function run a multithreaded request by using the request function
        as callback in a thread pool. Arguments are the list elements and are 
        passed as batches.

        Parameters
        ----------
        elements : List[Any]
            List of the elements different between requests. These are passed 
            as batches to each of the threads.

        Returns
        -------
        results : List[Any]
            List of return values of each of the threads.
        """
        
        batches = np.array_split(elements, self.__config["N_PROCESS"])
        futures = [self.executor.submit(self.request, elem = elem, n_id = n_id) 
                   for n_id, elem in enumerate(batches)]
        results = [future.result() for future in as_completed(futures)]
        return results


    @abstractmethod
    def request(
            self,
            elem: List[Any],
            n_id: int
        ) -> Any:
        """
        This member function is thought of to be overrided upon inheritance 
        and it should contain all that a single thread needs to run. This 
        function should be thread safe if it is intended to be used with 
        more than a single thread.

        Parameters
        ----------
        elem : List[Any]
            List of the elements different between requests.
        n_id : int
            Thread ID.
            
        Returns
        -------
        any : Any
            Any return, including None.
        """

        pass
