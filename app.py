"""
Gradio web interface for Vestaboard message sender.
Allows users to send and read messages from their Vestaboard.
"""

import gradio as gr
import argparse
import time
import signal
import sys
from vestaboard_client import VestaboardClient
from llm_client import LLMClient
from config import LLM_MODELS
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

        # Initialize LLM client (lazy loading - will initialize on first use)
        self.llm_client = None
        self.current_llm_model = None

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

    def test_color_bits(self) -> str:
        """
        Test all color tiles on the Vestaboard.

        Returns:
            Status message
        """
        if not self.client:
            return "Error: Client not initialized"

        result = self.client.test_color_bits()
        return result['message']

    def display_metals_prices(self) -> str:
        """
        Fetch and display Gold and Silver prices on the Vestaboard.

        Returns:
            Status message
        """
        if not self.client:
            return "Error: Client not initialized"

        result = self.client.display_metals_prices()
        return result['message']

    def initialize_llm(self, model_name: str) -> str:
        """
        Initialize or change the LLM model.

        Args:
            model_name: Name of the model to load

        Returns:
            Status message
        """
        try:
            if self.llm_client and self.current_llm_model == model_name:
                return f"Model {model_name} already loaded"

            self.llm_client = LLMClient(model_name)
            result = self.llm_client.initialize()

            if result['status'] == 'success':
                self.current_llm_model = model_name
                return f"✓ {result['message']}"
            else:
                return f"✗ {result['message']}"

        except Exception as e:
            return f"Error loading model: {str(e)}"

    def chat_with_ai(self, user_question: str, model_name: str) -> Tuple[str, str]:
        """
        Send question to AI and display response on Vestaboard.

        Args:
            user_question: User's question for the AI
            model_name: Selected model name

        Returns:
            Tuple of (AI response, Vestaboard status)
        """
        if not user_question or user_question.strip() == "":
            return "Please enter a question", "No message to send"

        # Initialize model if needed
        if not self.llm_client or self.current_llm_model != model_name:
            init_status = self.initialize_llm(model_name)
            if "Error" in init_status or "✗" in init_status:
                return f"Model initialization failed: {init_status}", "Model not ready"

        # Generate AI response
        try:
            result = self.llm_client.generate_response(user_question, max_length=132)

            if result['status'] != 'success':
                return f"Error: {result['message']}", "AI generation failed"

            ai_response = result['response']

            # Send to Vestaboard
            if self.client:
                vb_result = self.client.send_message(ai_response)
                vb_status = vb_result['message']
            else:
                vb_status = "Vestaboard client not initialized"

            return ai_response, vb_status

        except Exception as e:
            return f"Error: {str(e)}", "Failed to process request"

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

            with gr.Row():
                with gr.Column():
                    color_test_btn = gr.Button("Test Color Bits", variant="secondary")
                    color_test_output = gr.Textbox(
                        label="Color Test Status",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    metals_btn = gr.Button("Display Precious Metals Prices", variant="primary")
                    metals_output = gr.Textbox(
                        label="Metals Price Status",
                        interactive=False,
                        lines=4
                    )

            gr.Markdown("---")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### AI Chat to Vestaboard")
                    gr.Markdown("Ask a question and the AI response will be sent to your Vestaboard")

                    model_dropdown = gr.Dropdown(
                        choices=list(LLM_MODELS.keys()),
                        value=list(LLM_MODELS.keys())[0],
                        label="Select AI Model",
                        info="Choose which model to use for generating responses"
                    )

                    load_model_btn = gr.Button("Load Model", variant="secondary")
                    model_status = gr.Textbox(
                        label="Model Status",
                        interactive=False,
                        lines=2
                    )

                    chat_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask the AI anything...",
                        lines=3,
                        max_lines=5
                    )

                    chat_btn = gr.Button("Ask AI & Send to Vestaboard", variant="primary")

                    with gr.Row():
                        with gr.Column():
                            ai_response_output = gr.Textbox(
                                label="AI Response",
                                lines=6,
                                interactive=False
                            )
                        with gr.Column():
                            vestaboard_status_output = gr.Textbox(
                                label="Vestaboard Status",
                                lines=6,
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
            - Vestaboard displays up to 6 rows of 22 characters each (132 characters total)
            - Messages will be automatically formatted to fit the display
            - Use the "Test Connection" button to verify your Vestaboard is accessible
            - Use the "Test Color Bits" button to test all positions with color tiles (codes 63-71)
            - Use the "Display Precious Metals Prices" button to fetch and show Gold/Silver prices from Kitco
            - **AI Chat**: Load a model first, then ask questions. Responses are auto-truncated to 132 characters
            - Model loading may take 1-2 minutes on first run (downloads from HuggingFace)
            - Current board content shows the raw character codes
            """)

            # Wire up the event handlers
            connection_btn.click(
                fn=self.test_connection,
                outputs=connection_output
            )

            color_test_btn.click(
                fn=self.test_color_bits,
                outputs=color_test_output
            )

            metals_btn.click(
                fn=self.display_metals_prices,
                outputs=metals_output
            )

            # AI Chat event handlers
            load_model_btn.click(
                fn=self.initialize_llm,
                inputs=model_dropdown,
                outputs=model_status
            )

            chat_btn.click(
                fn=self.chat_with_ai,
                inputs=[chat_input, model_dropdown],
                outputs=[ai_response_output, vestaboard_status_output]
            )

            # Enter key shortcut for AI chat
            chat_input.submit(
                fn=self.chat_with_ai,
                inputs=[chat_input, model_dropdown],
                outputs=[ai_response_output, vestaboard_status_output]
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


def headless_mode():
    """
    Run in headless mode - updates precious metals prices at the top of every minute.
    """
    print("\n" + "="*50)
    print("Vestaboard Controller - Headless Mode")
    print("Updating precious metals prices at the top of each minute")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")

    app = VestaboardApp()

    if not app.client:
        print("ERROR: Failed to initialize Vestaboard client")
        print("Check your configuration in config.py")
        sys.exit(1)

    # Flag to handle graceful shutdown
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print("\n\nShutting down gracefully...")
        running = False

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    update_count = 0

    # Calculate seconds until the next top of the minute
    current_time = time.time()
    seconds_into_minute = current_time % 60
    seconds_until_next_minute = 60 - seconds_into_minute

    print(f"Waiting {seconds_until_next_minute:.1f} seconds until next top of minute...")
    print(f"First update will occur at {time.strftime('%H:%M:00', time.localtime(current_time + seconds_until_next_minute))}\n")

    # Wait until the top of the next minute (check running flag every 0.1 seconds for responsiveness)
    wait_time = 0
    while wait_time < seconds_until_next_minute and running:
        time.sleep(0.1)
        wait_time += 0.1

    # Main update loop - runs at the top of each minute
    while running:
        update_count += 1
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Update #{update_count}")

        try:
            result = app.client.display_metals_prices()

            if result['status'] == 'success':
                print(f"  ✓ {result['message']}")
            else:
                print(f"  ✗ {result['message']}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

        # Wait 60 seconds before next update (check running flag every 0.1 seconds for responsiveness)
        for _ in range(600):  # 600 * 0.1 = 60 seconds
            if not running:
                break
            time.sleep(0.1)

    print("\nStopped.")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Vestaboard Controller - Send messages and display information on your Vestaboard'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no GUI) - automatically update precious metals prices every minute'
    )
    parser.add_argument(
        '--metals',
        action='store_true',
        help='Alias for --headless (displays precious metals prices every minute)'
    )

    args = parser.parse_args()

    # Run in headless mode if requested
    if args.headless or args.metals:
        headless_mode()
        return

    # Otherwise, run the GUI
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
