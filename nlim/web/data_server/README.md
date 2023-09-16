# Running

Compile and launch the middleware server:
```
tsc server.ts
node server.js
```

Launch the data generator:
```
python data_generator.py
```

Launch an example client that will receive messages passed forward by the
middleware:
```
python example_client.py
```

Launch the signal processor endpoint:
```
python signal_processor.py
```
