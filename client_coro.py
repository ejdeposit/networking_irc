#client
import asyncio
import sys
import ast

def new_msgObj(msg):
    msgObj={}
    msgObj['contents']= msg
    return msgObj

def msgObj_to_str(msgObj):
    return str(msgObj)

def str_to_msgObj(msgStr):
    return ast.literal_eval(msgStr)

async def send_to_server(writer, loop):
    while True:
        line= await loop.run_in_executor(None, sys.stdin.readline)
        if line:
            line=line[:-1:]
            #make msgObj
            msgObj=new_msgObj(line)
            msgStr=msgObj_to_str(msgObj)
            writer.write(msgStr.encode())
            line=None

async def listen_to_server(reader):
    while True:
        data = await reader.read(100)
        if data:
            print(data.decode())
            await asyncio.sleep(0)


async def main(loop):
    #opens connection to server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888, loop=loop)

    await asyncio.gather(listen_to_server(reader), send_to_server(writer, asyncio.get_running_loop()))

    #closes connection
    print('Close the socket')
    writer.close()


#problem: this client sends message and then closes loop.  need to listen
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()

#loop.run_until_complete(tcp_echo_client(loop))
#try:
    #loop.run_forever()
#except KeyboardInterrupt:
#    pass
#loop.close()
