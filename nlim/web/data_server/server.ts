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

const window_length: number = 128
const num_channels: number = 32 // On the device
let rolling_window: number[][] = []
for (let i: number = 0; i < num_channels; i++) {
    rolling_window[i] = Array<number>()
}
// Buffer has been fully filled (and will continue to be)
let buffer_full: boolean = false

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
                messageBuffer = messageBuffer.slice(messageLength)
                messageLength = -1

                let data_dicts: Array<{[key: string]: Array<number>}> = decoded_data["d"]
                for (const data_dict of data_dicts) {
                    if (!("data" in data_dict)) {
                        continue;
                    }

                    let data_row: Array<number> = data_dict["data"]
                    for (const [index, val] of data_row.entries()) {
                        // If we've already sent a window, remove old data
                        if (buffer_full) {
                            rolling_window[index].shift()
                        }
                        rolling_window[index].push(val)
                    }
                }

                // Check if window is full, skip send if not
                if (!buffer_full) {
                    let buffers_full: number = 0
                    for (const channel_row of rolling_window) {
                        if (channel_row.length >= window_length) {
                            buffers_full += 1
                        }
                    }
                    buffer_full = (buffers_full === num_channels)

                    if (!buffer_full) {
                        return;
                    }
                }

                // Send data
                const data_to_send: string = JSON.stringify(rolling_window)
                console.log(`sending data`)

                client_endpoint.clients.forEach(
                    (client: ws.WebSocket) => {
                        if (client.readyState === ws.OPEN) {
                            client.send(data_to_send);
                        }
                    }
                );

            }
          });
    }
);

data_endpoint.listen(9000, () => {
  console.log('Server is listening on port 9000');

});
