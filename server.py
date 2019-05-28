import asyncio
import ast

#addressList is list of all client port numbers(int)
addressList=[]

#mailbox is dictionary each client port number is key to list of their 
#undelivered messages
mailBox={}

#chatRooms is dictionary. name or number of chatroom is key to list of
#client ports in chatroom.  server will iterate through a chat room's list
#and deliver message to each mailbox of each client in list.  Clients will 
#have to maintain their own list of what rooms they are in on their side.
ChatRooms={}

def is_connected():
    #need some way to determine if client is still connected.  if not 
    #terminate connection and cancel coroutines maybe.  probably a built 
    #in method for for checking.  Definitly build in method for canceling
    #coroutines
    pass

def delete_client(clientPort):
    #remove client from chatRooms lists and addressList
    pass

def remove_from_room(clientPort, room):
    #remove client from specificed chatroom list in chatroom dictionary
    pass

def add_to_room(clientPort, room):
    #add client from specificed chatroom list in chatroom dictionary
    pass

def new_msgObj(msg):
    #can add client name to msgObj on client side. server adds port number
    #on its side
    msgObj={}
    msgObj['contents']= msg
    return msgObj

def msgObj_to_str(msgObj):
    return str(msgObj)

def str_to_msgObj(msgStr):
    return ast.literal_eval(msgStr)

def new_client(port):
    global addressList
    global mailBox

    print('adding port', port) 
    if port not in addressList:
        addressList.append(port)
    if port not in mailBox:
        mailBox[port]=[]       
    #print('address list: ', addressList)

def broadcast_msg(msgObj):
    global addressList
    global mailBox

    for port in addressList:
        if msgObj['from'] != port:
            msg=str(msgObj['from']) + ': ' + msgObj['contents']
            mailBox[port].append(msg)

def check_mail(port):
    global addressList
    global mailBox

    if(mailBox[port]):
        msg= mailBox[port].pop(0)
        print('retreiving: ',msg)
        return msg
    return None

async def listen_to_client(reader, addr):
    while True:
        data = await reader.read(100)
        msgStr = data.decode()
        if msgStr:
            #add condional branching here to determine if string is 
            #broadcast msg, room specific, or command for server
            #e.g. change rooms

            print("Received %r" % (msgStr))
            msgObj= str_to_msgObj(msgStr)

            #adding port number to msgObj
            msgObj['from']=addr[1]
            broadcast_msg(msgObj)

async def send_to_client(writer, addr):
    while True:
        msgOut= check_mail(addr[1])
        if msgOut:
            writer.write(msgOut.encode())
            await writer.drain()
            msgOut=None
        await asyncio.sleep(0)

async def main(reader, writer):
    global addressList

    addr = writer.get_extra_info('peername')
    new_client(addr[1])

    await asyncio.gather(listen_to_client(reader, addr), send_to_client(writer, addr))

    print("Close the client socket")
    writer.close()

#127.0.0.1 is local host
loop = asyncio.get_event_loop()
coro = asyncio.start_server(main, '127.0.0.1', 8888, loop=loop)
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