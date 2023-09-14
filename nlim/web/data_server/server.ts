import ws = require('ws');
import net = require('net');

/**
 * Decodes binary data into a JSON object.
 *
 * @param binaryData - The binary data to be decoded.
 * @returns The decoded JSON object.
 */
function decodeJsonBinary(binaryData: Uint8Array) {
  const decodedString: string = new TextDecoder().decode(binaryData);
  const decodedJson: {} = JSON.parse(decodedString);
  return decodedJson;
};

// Configure client endpoint
const client_endpoint = new ws.Server({ port: 8080, clientTracking: true });
client_endpoint.on('connection', (client_ws: ws.WebSocket) => {
  console.log(`[CLIENT ENDPOINT] New client connected ${client_ws}`);
  console.log(`[CLIENT ENDPOINT] Clients: ${client_endpoint.clients}`);
});


// Configure data endpoint
const data_endpoint = net.createServer(

    (socket: net.Socket) => {
        let messageLength: number = -1
        let messageBuffer: Buffer = Buffer.alloc(0)

        console.log(`socket ${socket}`)

        // Configure the socket to send data it receives to all clients
        // connected to the client endpoint
        socket.on('data', (data: Uint8Array) => {
            // Get the expected msg length if it's the first one
            if (messageLength == -1) {
                let SPACE_CHAR_CODE: number = 32
                let separator_index: number = data.indexOf(SPACE_CHAR_CODE)
                let length_as_number: string = String.fromCharCode.apply(null, data.slice(0, separator_index))
                messageLength = parseInt(length_as_number)
                console.log(`Stated message length is ${messageLength}`)

                data = data.slice(separator_index + 1)
            }

            messageBuffer = Buffer.concat([messageBuffer, data])

            if (messageBuffer.length >= messageLength) {
                const decoded_data: {} = decodeJsonBinary(messageBuffer)
                const data_to_send: string = JSON.stringify(decoded_data)

                client_endpoint.clients.forEach(
                    (client: ws.WebSocket) => {
                        if (client.readyState === ws.OPEN) {
                            client.send(data_to_send);
                        }
                    }
                );

                messageBuffer = messageBuffer.slice(messageLength)
                messageLength = -1
            }
          });
    }
);

data_endpoint.listen(9000, () => {
  console.log('Server is listening on port 9000');

});
