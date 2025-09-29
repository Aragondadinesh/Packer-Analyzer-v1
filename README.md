🏗️ Architecture

The system follows a modular pipeline where each service has a single responsibility:

Capture → Parser → Persistor → PostgreSQL ← Analyzer ← UI

Capture Service

Sniffs live network packets (requires NET_ADMIN + NET_RAW capabilities)

Or replays packets from .pcap files

Sends packet metadata as JSON to the Parser Service

Parser Service

Classifies packets into TCP, UDP, ICMP, DNS, etc.

Normalizes data into a common JSON format

Forwards JSON to the Persistor Service

Persistor Service

Inserts packet metadata into PostgreSQL

Maintains a packets table for analysis and queries

Analyzer Service

Reads data from PostgreSQL

Exposes REST APIs for analysis:

/protocol_summary → aggregated statistics by protocol

/packets → list of packets

/filter → filter packets by protocol, IP, etc.

UI Service

React-based web dashboard

Calls Analyzer APIs to fetch data

Displays live charts, tables, and summaries in the browser
