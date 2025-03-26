import pydivert

MARKET_SEARCH_START = "\x08\x05\xa5\x9c9R\xc0"
MARKET_SEARCH_END = "\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x1a\x18\x91\x11\xf0\x86\t8\xe3\xefE\xc6z\xbd-8\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06\x9fJ\x8ff\x95\x858\x06"

# Filter for TCP packets going to the target IP
FILTER = "tcp and tcp.DstPort == 12102 and tcp.PayloadLength > 0"
with pydivert.WinDivert(FILTER) as w:
    try:
        for packet in w:
            if packet.is_outbound:
                if str(packet.payload).startswith(MARKET_SEARCH_START):
                    search_value = str(packet.payload)[len(MARKET_SEARCH_START):-len(MARKET_SEARCH_END)]
                    print(f"Intercepted Market Search Request: {search_value}")
                    
                print(f"Intercepted Packet ({"INBOUND" if packet.is_inbound else "OUTBOUND"}): {packet.payload}")
            w.send(packet)  # Forward it normally
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)