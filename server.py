#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio, socket, json

connections = list()
adminSockets = []

async def handle_client(reader, writer):
  
  connection = writer._transport.get_extra_info('peername')
  connected = True  
  def disconnect_client():
  	remove_disconnections(connection, connections)
  	remove_disconnections(connection, adminSockets)
  	writer.close()

  while 1:
    try:
    	info = (await reader.readuntil(b'^')).decode('utf8').replace('^','')
    except:
    	disconnect_client()
    	break

    infoJson = is_json(info)
    connectionJson = {"address": ','.join(map(str,connection))}
    infoJson.update(connectionJson)
    connection_set_in(infoJson,connections)
    
    if info == '!DISCONNECT':
    	disconnect_client()
    	break
    
    if infoJson["role"] == "admin":
    	connection_set_in((connection,reader,writer),adminSockets)
    
    for addressbc,readerbc,writerbc in adminSockets:
    	connectionsString = str(connections).strip('[]').encode('utf8')
    	writerbc.write(connectionsString)
    
    writer.write(f'ok, received {info}'.encode('utf8'))
    await writer.drain()
  writer.close()

async def run_server():
  port = 15555
  #server = await asyncio.start_server(handle_client, 'localhost', port)
  server = await asyncio.start_server(handle_client, '144.126.212.229', port)
  async with server:
    print(f'Listening on localhost {port}')
    await server.serve_forever()

def is_json(someJSON):
  try:
    json_object = json.loads(someJSON)
  except ValueError as e:
    return False
  return json_object

def connection_set_in(incoming, existingList):
	exists = False
	if not existingList:
		existingList.append(incoming)
	else:
		#listSet = set(existingList)
		for i in existingList:
			if incoming == i:
				exists = True
		if exists == False:
			return existingList.append(incoming)

def remove_disconnections(address, existingList):
	removed = -1
	addressStr = ','.join(map(str,address))
	for i, item in enumerate(existingList):
		if addressStr in item or addressStr: #== item["address"]:
			removed = i
			break
	if removed != -1:
		existingList.pop(removed)

asyncio.run(run_server())