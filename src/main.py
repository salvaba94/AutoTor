from autotor import TorIP


if __name__ == "__main__":

    with TorIP() as tor:
        for i in range(5):
            ip = tor.request()
            print("Tor IP is: ", ip)
     

