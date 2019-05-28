import asyncio

addressList=[]
mailBox={}
#server

def new_client(port):
    global addressList
    global mailBox

    print('adding port', port) 
    #add port to addressList
    if port not in addressList:
        addressList.append(port)
    if port not in mailBox:
        mailBox[port]=[]       

    #set up mailbox
    print('address list: ', addressList)

def broadcast_msg(msg):
    global addressList
    global mailBox

    for port in addressList:
        mailBox[port].append(msg)

def check_mail(port):
    global addressList
    global mailBox

    if(mailBox[port]):
        msg= mailBox[port].pop(0)
        print('retreiving: ',msg)
        return msg

async def listen_to_client(reader, addr):
    while True:
        data = await reader.read(100)
        message = data.decode()
        print("Received %r" % (message))
        broadcast_msg(message)

async def send_to_client(writer, addr):
    while True:
        msgOut= check_mail(addr[1])
        if msgOut:
            writer.write(msgOut.encode())
            await writer.drain()
            msgOut=None
        await asyncio.sleep(0)

async def handle_echo(reader, writer):
    global addressList

    addr = writer.get_extra_info('peername')
    new_client(addr[1])

    await asyncio.gather(listen_to_client(reader), send_to_client(writer, addr))

    print("Close the client socket")
    writer.close()

#127.0.0.1 is local host
loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()