# Secure Data Transmission Project

This project implements a secure data transmission system using public channels. It includes functionalities for data hiding, fragmentation, and synchronization between sender and receiver without direct communication.

## Project Structure

```
secure-data-transmission
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── channel
│   │   ├── __init__.py
│   │   ├── onenet_channel.py
│   │   └── other_channel.py
│   ├── steganography
│   │   ├── __init__.py
│   │   ├── lsb.py
│   │   └── dct.py
│   ├── fragmentation
│   │   ├── __init__.py
│   │   ├── fragmenter.py
│   │   └── reassembler.py
│   └── sync
│       ├── __init__.py
│       └── sync_mechanism.py
├── tests
│   ├── __init__.py
│   └── test_basic.py
├── requirements.txt
├── setup.py
└── README.md
```

## Features

1. **Channel Construction**: The project supports at least two public transmission channels. OneNet channel is implemented, and users can add other channels as needed.
  
2. **Data Hiding**: 
   - **LSB (Least Significant Bit)**: Users can choose the number of color channels (RGB) and the number of least significant bits to replace.
   - **DCT (Discrete Cosine Transform)**: Users can select the number of color channels (YUV) and the number of pixel pairs to swap in each 8x8 block.

3. **Data Fragmentation**: The sender can fragment data into at least two channels for transmission. The receiver can retrieve and reassemble the fragmented data.

4. **Synchronization Mechanism**: A predefined synchronization mechanism is established between the sender and receiver to ensure proper communication without direct contact.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

1. Configure the channels and data hiding parameters in `main.py`.
2. Run the application to initiate the data transmission process.
3. Ensure that the sender and receiver follow the agreed synchronization mechanism for successful data exchange.

## Testing

Basic functionality tests are included in the `tests/test_basic.py` file. Run the tests to verify that all modules are functioning correctly.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.