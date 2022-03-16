# AutoTor

<div id="top"></div>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- TOC -->
<details open=true>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the Project</a>
       <ul>
        <li><a href="#contents">Contents</a></li>
        <li><a href="#dependencies">Dependencies</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#coding">Coding</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>
<!-- /TOC -->


<!-- ABOUT -->
## About the Project
Simple high-level API to make parallel requests throughout Tor in an automated way, with circuit renewal and randomised user-agents. It can be used to easily navigate in an anonymus way or to get information from webs. At the moment, AutoTor is not OS-agnostic as it is tailored to Windows but is expected to become compatible with, at least, Linux in the short-term.

### Contents
The most important source code elements in the project are outlined and described as follows:
* ```main.py```: Implements an example of how the library should be used.
* AutoTor module:
  * ```autotor_base.py```: Implements a class that takes care of all the logic to automate Tor download, Tor configuration, Tor initialisation, getting request sessions, Tor circuit renewal, releasing Tor resources and performing parallel runs with a pool of threads.
  * ```autotor_ip.py```: Implements an example class to override the request function that actually takes care of the requests. In this case, the function tries to get the IP in use by Tor. 

<p align="right"><a href="#top">Back to top</a></p>

### Dependencies
Among others, the project has been built around the following Python libraries:

* [requests[socks]][requests-link] (>=2.27.1)
* [stem][stem-link] (>=1.8.0) 
* [fake-useragent][fake-useragent-link] (>=0.1.11)

<p align="right"><a href="#top">Back to top</a></p>
<!-- /ABOUT -->


<!-- START -->
## Getting Started
### Installation

#### Option 1 - setup.py
To install with ```pip``` by using the setup.py, one should just follow two steps:
1. Clone the project:
```bash
  git clone https://github.com/salvaba94/AutoTor.git
```
2. Run the following command to install the dependencies and AutoTor:
```bash
  pip install .
```

<p align="right"><a href="#top">Back to top</a></p>

#### Option 2 - PyPI
Installing AutoTor from PyPI is the simplest. It only requires the following command:

```bash
  pip install autotor
```

<p align="right"><a href="#top">Back to top</a></p>

### Coding

#### Create your class
The main class of the package is ```TorRequests```. It is a class with an abstract method ```request``` that should be implemented in any derived class to customise the request as desired by the user. ```TorIP``` is an example class illustrating how the derived class could be potentially implemented. Below is the metacode for a sample implementation:

```python
from autotor import TorRequests
from threading import Lock

GLOBAL_LOCK = Lock()

class MyClass(TorRequests):

    # Override the initialisation function (if needed).
    def __init__(self, another_arg = 5, *args, **kwargs):
        # Initialise superclass.
        super(MyClass, self).__init__(*args, **kwargs)
        # Initialise other parameters.
        self.another_arg = another_arg

    # Override the request function and implement custom functionality. 
    # This function gets as inputs the elements the current thread should 
    # take care of and the ID of the current thread. Naturally, the 
    # function should be thread-safe.
    def request(self, elem, n_id):
        
        # Get Tor session.
        session = self.get_tor_session(n_id)
        # Renew Tor circuit.
        self.renew_tor_ip(n_id)

        # Use the session to get information.
        # Use elem to characterise the differences between requests.
        # Use GLOBAL_LOCK to handle non-atomic operations.
        ...
```
**Note**: In order to make the requests with another IP and user-agent just get another session and call the renew method. It is also recommended to randomise the waiting time between requests.

<p align="right"><a href="#top">Back to top</a></p>

#### Usage
Once one has implemented the request method in the derived class, one can use the threaded request version within a ```with``` statement to implicitly call the request method. Any opened resources will be automatically cleared upon exiting the statement.

```python
from autotor import MyClass
import numpy as np

# Use threaded_request within a with statement. This function will 
# take care of allocating the list of requests among the thread pool.
with MyClass(another_arg = 20, n_process = 5, tor_root = ".") as tor:
    result = tor.threaded_request(np.arange(10))
```

<p align="right"><a href="#top">Back to top</a></p>

<!-- /START -->

<!-- CONTRIBUTING -->
## Contributing

Any contributions are greatly appreciated. If you have suggestions that would make the project any better, fork the repository and create a pull request or simply open an issue. If you decide to follow the first procedure, here is a reminder of the steps:

1. Fork the project.
2. Create your branch:
```
  git checkout -b branchname
```
3. Commit your changes:
```
  git commit -m "Add some amazing feature"
```
4. Push to the branch: 
```
  git push origin branchname
```
5. Open a pull request.

<p align="right"><a href="#top">Back to top</a></p>

**Disclaimer:** The authors won't be hold accountable of any irresponsible misuse of the high-level API as per the [MIT License][license-url]. So, use it with care.

**If you like the project and/or any of its contents results useful to you, don't forget to give it a star in [GitHub][github-repo]! It means a lot to me .**

<!-- LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/salvaba94/AutoTor.svg?style=plastic&color=0e76a8
[contributors-url]: https://github.com/salvaba94/AutoTor/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/salvaba94/AutoTor.svg?style=plastic&color=0e76a8
[forks-url]: https://github.com/salvaba94/AutoTor/network/members
[stars-shield]: https://img.shields.io/github/stars/salvaba94/AutoTor.svg?style=plastic&color=0e76a8
[stars-url]: https://github.com/salvaba94/G2Net/stargazers
[issues-shield]: https://img.shields.io/github/issues/salvaba94/AutoTor.svg?style=plastic&color=0e76a8
[issues-url]: https://github.com/salvaba94/AutoTor/issues
[license-shield]: https://img.shields.io/github/license/salvaba94/AutoTor.svg?style=plastic&color=0e76a8
[license-url]: https://github.com/salvaba94/AutoTor/blob/main/LICENSE
[stem-link]: https://stem.torproject.org/
[requests-link]: https://docs.python-requests.org/en/latest/
[fake-useragent-link]: https://github.com/hellysmile/fake-useragent
[github-repo]: https://github.com/salvaba94/AutoTor

<!-- /LINKS -->
