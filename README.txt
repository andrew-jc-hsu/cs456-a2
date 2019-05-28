README

Overview:
- Written for CS 458 Computer Networks W19, taught by Dr. N. Limam.
- The assignment specification asks for:
A sender program, that reads data from a given file and sends it in numbered data packets using Go-Back-N protocol to the network emulator. 
A receiver program, that receives data packets from the network emulator and sends back ACK packets after checking their sequence numbers.
A network emulator that may delay or drop packets (provided).
Certain packet formats are enforced (provided).
- I realize that I did not modularize this one very well. That's on me. This was corrected in assignment 3.


Built on ubuntu1604-006
Tested on ubuntu1604-006
Compiler: python 2.7.12

No makefile needed b/c Python

Run each program as follows:
1. nEmulator <emulator's receiving UDP port for sender> <receiver's network address> <receiver's receiving UDP port>
	<emulator's receiving UDP port for receiver> <sender's network address> <sender's receiving UDP port>
	<max delay of link in ms> <packet discard probability>
2. python receiver.py <emulator hostname> <emulator port to send to> <rcvr port to recv> <output file>
3. python sender.py <emulator hostname> <emulator port to send to> <sender port to recv> <input file>

Misc notes:
- The Java classes have been foregone in favour of a python struct.pack()/unpack() solution.
- There is a slightly ugly part in sender.py, using an empty_case flag variable to prevent deadlock when the sent file is empty.
- Receiver will send an ACK with number 31 if it receives a packet with seqnum != 0 (ie. packet 0 was dropped).
- Sometimes, the final "EOT" packet sent by the receiver has type 0 (from invalid seqnum received) instead of type 2, but this does not seem to affect the correctness of the programs. Both programs still terminate properly.

