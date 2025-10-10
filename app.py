"""
Gradio web interface for Vestaboard message sender.
Allows users to send and read messages from their Vestaboard.
"""

import gradio as gr
from vestaboard_client import VestaboardClient
from typing import Tuple


class VestaboardApp:
    """Main application class for the Gradio interface."""

    def __init__(self):
        """Initialize the Vestaboard application."""
        try:
            self.client = VestaboardClient()
            self.connection_status = "Initializing..."
        except Exception as e:
            self.client = None
            self.connection_status = f"Error initializing: {str(e)}"

    def test_connection(self) -> str:
        """Test connection to Vestaboard."""
        if not self.client:
            return "Error: Client not initialized"

        result = self.client.test_connection()
        self.connection_status = result['message']
        return self.connection_status

    def send_message(self, message: str) -> str:
        """
        Send a message to the Vestaboard.

        Args:
            message: Text message to send

        Returns:
            Status message
        """
        if not self.client:
            return "Error: Client not initialized"

        if not message or message.strip() == "":
            return "Error: Please enter a message"

        result = self.client.send_message(message)
        return result['message']

    def read_message(self) -> str:
        """
        Read the current message from the Vestaboard.

        Returns:
            Current board content or error message
        """
        if not self.client:
            return "Error: Client not initialized"

        result = self.client.read_message()
        if result['status'] == 'success':
            # Format the board data for display
            board_data = result['data']
            if board_data:
                return f"Current board content:\n{self._format_board_data(board_data)}"
            else:
                return "Board is empty"
        else:
            return result['message']

    def _format_board_data(self, board_data) -> str:
        """
        Format board data for display.

        Args:
            board_data: Raw board data from the API

        Returns:
            Formatted string representation
        """
        # The board data is typically a 2D array of character codes
        # For now, return a simple representation
        if isinstance(board_data, list):
            return f"Board data (character codes):\n{board_data}"
        else:
            return str(board_data)

    def create_interface(self) -> gr.Blocks:
        """
        Create and configure the Gradio interface.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title="Vestaboard Controller", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# Vestaboard Message Controller")
            gr.Markdown("Send and read messages from your Vestaboard device")

            with gr.Row():
                with gr.Column():
                    connection_btn = gr.Button("Test Connection", variant="secondary")
                    connection_output = gr.Textbox(
                        label="Connection Status",
                        value=self.connection_status,
                        interactive=False
                    )

            gr.Markdown("---")

            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Send Message")
                    message_input = gr.Textbox(
                        label="Message",
                        placeholder="Enter your message here...",
                        lines=3,
                        max_lines=10
                    )
                    send_btn = gr.Button("Send to Vestaboard", variant="primary")
                    send_output = gr.Textbox(
                        label="Send Status",
                        interactive=False
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### Read Current Message")
                    read_btn = gr.Button("Read from Vestaboard", variant="secondary")
                    read_output = gr.Textbox(
                        label="Current Board Content",
                        lines=10,
                        interactive=False
                    )

            gr.Markdown("---")
            gr.Markdown("""
            ### Quick Tips:
            - Vestaboard displays up to 6 rows of 22 characters each
            - Messages will be automatically formatted to fit the display
            - Use the "Test Connection" button to verify your Vestaboard is accessible
            - Current board content shows the raw character codes
            """)

            # Wire up the event handlers
            connection_btn.click(
                fn=self.test_connection,
                outputs=connection_output
            )

            send_btn.click(
                fn=self.send_message,
                inputs=message_input,
                outputs=send_output
            )

            read_btn.click(
                fn=self.read_message,
                outputs=read_output
            )

            # Add Enter key shortcut for sending messages
            message_input.submit(
                fn=self.send_message,
                inputs=message_input,
                outputs=send_output
            )

        return interface


def main():
    """Main entry point for the application."""
    app = VestaboardApp()
    interface = app.create_interface()

    print("\n" + "="*50)
    print("Starting Vestaboard Controller...")
    print("="*50 + "\n")

    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",  # Allow access from network
        server_port=7860,
        share=False,  # Set to True if you want a public URL
        inbrowser=True  # Automatically open browser
    )


if __name__ == "__main__":
    main()
