FROM wakuorg/nwaku:v0.35.0

ENTRYPOINT [ \
  "/usr/bin/wakunode", \
  "--nat=extip:127.0.0.1", \
  "--peer-exchange=true", \
  "--rest-address=0.0.0.0", "--rest-admin", \
  "--keep-alive=true", "--max-connections=18000", \
  "--discv5-discovery=true", "--discv5-enr-auto-update=True", \
  "--cluster-id=16", "--shard=32", "--shard=64", \
  "--tcp-port=60000", "--discv5-udp-port=9000", \
  "--log-level=DEBUG", \
  # Docker DNS server
  "--dns-addrs-name-server=127.0.0.11" \ 
]
