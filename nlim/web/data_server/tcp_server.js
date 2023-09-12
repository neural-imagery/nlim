function decodeJsonBinary(encodedData) {
  // Convert the encoded data to a Uint8Array
  const binaryData = new Uint8Array(encodedData);

  // Decode the binary data as a string
  const decodedString = new TextDecoder().decode(binaryData);

  // Parse the decoded string as JSON
  const decodedJson = JSON.parse(decodedString);

  return decodedJson;
}
/*
server.listen(9000, function() {
  console.log('server listening to %j', server.address());
});

function handleConnection(conn) {
  var remoteAddress = conn.remoteAddress + ':' + conn.remotePort;
  console.log('new client connection from %s', remoteAddress);

  conn.on('data', onConnData);
  conn.once('close', onConnClose);
  conn.on('error', onConnError);

  function decodeJsonBinary(encodedData) {
      // Convert the encoded data to a Uint8Array
      const binaryData = new Uint8Array(encodedData);

      // Decode the binary data as a string
      const decodedString = new TextDecoder().decode(binaryData);

      // Parse the decoded string as JSON
      const decodedJson = JSON.parse(decodedString);

      return decodedJson;
  }

  function onConnData(d) {
    const timestamp = new Date().toLocaleString(); // Get the current date and time as a string
    // console.log(`[${timestamp}] ${message}`);
    console.log('[%s] connection data from %s: %j', timestamp, remoteAddress, d);
    decoded_data = decodeJsonBinary(d)
    console.log('[%s] decoded data is %s: %j', timestamp, remoteAddress, d);

    conn.write(d);
  }

  function onConnClose() {
    console.log('connection from %s closed', remoteAddress);
  }

  function onConnError(err) {
    console.log('Connection %s error: %s', remoteAddress, err.message);
  }
}
*/
const net = require('net');

const server = net.createServer((socket) => {
  let dataBuffer = Buffer.alloc(0); // Buffer to store incoming data
  let messageLength = -1

  socket.on('data', (data) => {
    // Append the received data to the buffer
    dataBuffer = Buffer.concat([dataBuffer, data.slice(4)]);
    console.log(data)
    console.log(data.length)

    if (messageLength == -1) {
        function parseJsonBuffer(jsonBuffer) {
          let jsonString = '';
          let i = 0;

          while (i < jsonBuffer.length && jsonBuffer[i] !== "\\") { // 10 represents the newline character
            new_char = String.fromCharCode(jsonBuffer[i]);
            jsonString += new_char
            console.log(new_char)
            i++;
          }

          console.log(`json string is ${jsonString}`)
          const parsedInt = parseInt(jsonString);

          return parsedInt;
        }

        messageLength = parseJsonBuffer(dataBuffer)
        console.log(`message length is ${messageLength}`)
    }


    // Check if the complete message has been received
    if (dataBuffer.length >= messageLength) {
        // Extract the complete message from the buffer
        const message = dataBuffer.slice(4, 4 + messageLength);

        // Process the complete message
        const decoded_msg = decodeJsonBinary(message)
        console.log('Received message:', decoded_msg);

        // Remove the processed message from the buffer
        dataBuffer = dataBuffer.slice(4 + messageLength);
    }
  });
});

server.on('error', (err) => {
  console.error('Server error:', err);
});

server.listen(9000, () => {
  console.log('Server is listening on port 9000');
});
