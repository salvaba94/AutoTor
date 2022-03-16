from autotor import TorIP
import numpy as np
import time


if __name__ == "__main__":

    n_request = 10
    n_process = 5

    with TorIP(n_process = n_process) as tor:
        init = time.time()
        results = tor.threaded_request(np.arange(n_request))
        elapsed = time.time() - init

    print()
    print("Running time is " + "{:.2f}".format(elapsed / n_request) + 
          " seconds/request")
     

