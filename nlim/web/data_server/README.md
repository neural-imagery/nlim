# Running

Launch the platform server
```
python server.py
```

Launch the device endpoint:
```
python device_data_server.py
```

# Adding New Processors

A `Processor` is something that reads channel data from the device and returns
some processed result for consumption by a downstream (e.g., frontend) system.

See `processors/processor.py` for the exact API, and concrete implementations in
the same directory for examples.

After adding a new `Processor` subclass, hook it up to the server by adding an
instance of the class to `path_to_processor`, along with a path that clients can
use to subscribe to the processed data stream.

You can now subscribe to the new processed data stream using
`ws://host:port/<your_path>`
