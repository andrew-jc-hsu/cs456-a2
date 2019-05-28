#!/usr/bin/env python

from socket import *
import struct, sys

# 0. Usage and argument initialization
if ( len( sys.argv ) != 5 ):
	sys.exit( "Usage: " + sys.argv[0] + " <emulator hostname> <UDP port to send ACKs to> <UDP port to receive data from> <file to write into>" )

emu_hostname = sys.argv[1]
emu_port = int( sys.argv[2] )
receive_port = int( sys.argv[3] )

filename = open( sys.argv[4], "w" )
arrival_log = open( "arrival.log", "w" )
expected_seqnum = 0
receiverSocket = socket( AF_INET, SOCK_DGRAM )
receiverSocket.bind( ('', receive_port ) )

# 1. Receiving packets
while ( True ):
	packet, addr = receiverSocket.recvfrom( 512 ) # Receive a packet
	ptype, pseqnum, plength, pdata = struct.unpack( '!iii500s', packet )
	pdata = pdata[0:plength] # Remove any padded null bytes
	arrival_log.write( str( pseqnum )+"\n" ) # Log the packet's seqnum

	if ( ptype == 2 ): # If packet is of type EOT
		eot = struct.pack( '!iii500s', 2, expected_seqnum, 0, '' )
		receiverSocket.sendto( eot, ( emu_hostname, emu_port ) ) # Send EOT packet
		break # End the receiving loop
	elif ( pseqnum == expected_seqnum ): # Expected packet seqnum
		filename.write( pdata ) # Write data into filename
		ack = struct.pack( '!iii500s', 0, pseqnum, 0, '' )
		receiverSocket.sendto( ack, ( emu_hostname, emu_port ) ) # Send ACK seqnum
		expected_seqnum = (expected_seqnum + 1) % 32 # Update expected_seqnum
	else: # Invalid packet seqnum
		# Discard packet (do nothing) and send ACK expected_seqnum - 1 % 32
		ack = struct.pack( '!iii500s', 0, (expected_seqnum - 1) % 32, 0, '' )
		receiverSocket.sendto( ack, ( emu_hostname, emu_port ) )
	# if
# while

# 2. Clean-up
filename.close()
arrival_log.close()
receiverSocket.close()
