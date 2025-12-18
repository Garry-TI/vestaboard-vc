# Vestaboard Controller

A Python application with a Gradio web interface for sending and reading messages from your local Vestaboard device.

## Features

- **Send Messages**: Send text messages to your Vestaboard with a simple web interface
- **Read Messages**: Retrieve the current message displayed on your Vestaboard
- **Test Connection**: Verify connectivity to your Vestaboard device
- **User-Friendly Interface**: Clean, intuitive Gradio web UI accessible from any browser

## Prerequisites

- Python 3.8 or higher
- A Vestaboard device on your local network
- Vestaboard Local API enabled and API key obtained

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Vestaboard credentials**:
   - Open `config.py`
   - Replace `YOUR_API_KEY_HERE` with your actual Vestaboard API key (the key you received after enabling Local API)
   - Verify the IP address matches your Vestaboard (currently set to `192.168.1.1`)

   ```python
   VESTABOARD_CONFIG = {
       'ip': '192.168.1.1',
       'api_key': 'your-actual-api-key-here'
   }
   ```

   **Note**: Use the API key you received after enabling the Local API, NOT the enablement token. The enablement token is only used once to enable the API and get the API key.

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   - The application will automatically open in your default browser
   - If not, navigate to `http://localhost:7860`

3. **Using the interface**:
   - **Test Connection**: Click to verify your Vestaboard is accessible
   - **Send Message**: Type your message and click "Send to Vestaboard" (or press Enter)
   - **Read Message**: Click "Read from Vestaboard" to see the current display

## Project Structure

```
vestaboard-vc/
├── app.py                  # Main Gradio application
├── vestaboard_client.py    # Vestaboard API wrapper
├── config.py              # Configuration file (contains your API token)
├── config.example.py      # Example configuration template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Vestaboard Message Format

- The Vestaboard display is 6 rows by 22 columns
- Messages are automatically formatted by the library
- Text is converted to uppercase and centered by default

## Troubleshooting

### Connection Issues

1. **Verify your Vestaboard is on the network**:
   ```bash
   ping <Vestaboard IP Address>
   ```

2. **Check your API key**:
   - Make sure you're using the API key (not the enablement token) in `config.py`
   - Verify Local API is enabled on your Vestaboard

3. **Firewall**: Ensure your firewall allows communication with the Vestaboard

### Common Errors

- **"Client not initialized"**: Check that your `config.py` has valid credentials
- **"Connection failed"**: Verify IP address and network connectivity
- **"Error sending message"**: Check API key validity and Local API access
- **"No host supplied"**: Make sure you're using the API key, not the enablement token

## API Reference

### VestaboardClient Methods

- `send_message(message: str)`: Send a text message to the board
- `read_message()`: Read the current board content
- `send_raw(character_codes: list)`: Send raw character codes for precise control
- `test_connection()`: Test connectivity to the device

## Security Notes

- `config.py` is excluded from git tracking (via `.gitignore`)
- Never commit your actual API token to version control
- Use `config.example.py` as a template for sharing

## Dependencies

- **gradio**: Web interface framework
- **vestaboard**: Official Vestaboard Python library

## License

This project is provided as-is for personal use with your Vestaboard device.

## Resources

- [Vestaboard API Documentation](https://docs.vestaboard.com/docs/read-write-api/)
- [Vestaboard Python Library](https://github.com/ShaneSutro/Vestaboard)
- [Gradio Documentation](https://gradio.app/docs/)
