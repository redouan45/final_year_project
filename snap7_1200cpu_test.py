import time
import snap7
import snap7.util as su
client = snap7.client.Client()

client.connect("192.168.0.1", 0, 2)


client.get_connected()
while True:
    counter = client.mb_read(2,2)
    print(counter)
    print(su.get_int(counter, 0))
    bits = bin(counter[1]).split('b')[1]
    while len(bits) <= 7:
        bits = "0" + bits
    print(bits)
    time.sleep(1)
