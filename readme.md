### Python NAT Traversal Test ###

Best run in python interactive mode, on two machines on seperate networks on the internet.

Start a client on each machine (cliA and cliB). This will run the stun lookup, and throw an exception if the NAT type is detected as too restrictive.
```python
from main import Client
cliA = Client()
```

Get the external ip and port for each client
```python
cliA.external_ip
>>> "11.22.33.44.55"
cliA.external_port
>>> 123456
```

Send a packet from one to the other
```python
cliB.put_packet("hello, is it me you're looking for?", ("11.22.33.44", 123456))
```

Check if the other client received the packet
```python
cliA.get_packet()
>>> ("hello, is it me you're looking for?", ("8.8.8.8", 8888))
```