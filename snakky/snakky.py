import reflex as rx
import uuid
from .db import init_db, add_message, get_conversation
from .llm import stream_chat


class ChatState(rx.State):
    """Chat state."""
    session_id: str = ""
    messages: list[dict] = []
    input_value: str = ""
    is_loading: bool = False

    def initialize_session(self):
        """Initialize session on page load."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

    def set_input(self, value: str):
        """Set input value."""
        self.input_value = value

    async def send_message(self):
        """Send user message and get AI response."""
        if not self.input_value.strip():
            return

        # Add user message
        user_msg = self.input_value
        self.input_value = ""
        self.is_loading = True
        
        await add_message(self.session_id, "user", user_msg)
        self.messages.append({"role": "user", "content": user_msg})

        # Build context for LLM
        context = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]

        # Stream AI response
        ai_response = ""
        async for chunk in stream_chat(context):
            ai_response += chunk

        # Save AI response to DB
        if ai_response:
            await add_message(self.session_id, "assistant", ai_response)
            self.messages.append({"role": "assistant", "content": ai_response})

        self.is_loading = False


def index() -> rx.Component:
    """Main chat page."""
    return rx.container(
        rx.center(
            rx.vstack(
                rx.heading("Snakky AI Chat"),
                rx.box(
                    rx.cond(
                        ChatState.messages.length() > 0,
                        rx.vstack(
                            rx.foreach(ChatState.messages, lambda msg: rx.box(
                                rx.box(
                                    rx.text(msg["content"]),
                                    padding="12px",
                                    bg=rx.cond(msg["role"] == "user", "#3b82f6", "#e5e7eb"),
                                    border_radius="8px",
                                    color=rx.cond(msg["role"] == "user", "white", "black"),
                                    max_width="70%",
                                ),
                                display="flex",
                                justify_content=rx.cond(msg["role"] == "user", "flex-end", "flex-start"),
                                width="100%",
                                margin_bottom="12px",
                            )),
                            width="100%",
                            spacing="2",
                        ),
                        rx.text("No messages yet. Start chatting!", color="#9ca3af"),
                    ),
                    width="100%",
                    min_height="400px",
                    max_height="400px",
                    overflow_y="auto",
                    border="1px solid #e5e7eb",
                    padding="16px",
                    border_radius="8px",
                    bg="#fafafa",
                ),
                rx.hstack(
                    rx.input(
                        placeholder="Type your message...",
                        value=ChatState.input_value,
                        on_change=ChatState.set_input,
                        width="100%",
                    ),
                    rx.button(
                        "Send",
                        on_click=ChatState.send_message,
                        is_loading=ChatState.is_loading,
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                max_width="600px",
            ),
        ),
        on_mount=ChatState.initialize_session,
        padding="32px",
    )


app = rx.App()
app.add_page(index)
