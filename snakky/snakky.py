import reflex as rx
import uuid
import asyncio
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

    async def load_conversation(self):
        """Load messages from DB."""
        if self.session_id:
            self.messages = await get_conversation(self.session_id)

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
            # Update UI in real-time
            self.messages[-1] = {"role": "user", "content": user_msg}
            # Emit a temporary AI message for streaming
            yield

        # Save AI response to DB
        if ai_response:
            await add_message(self.session_id, "assistant", ai_response)
            self.messages.append({"role": "assistant", "content": ai_response})

        self.is_loading = False


def chat_message(msg: dict) -> rx.Component:
    """Render a single message."""
    is_user = msg["role"] == "user"
    return rx.box(
        rx.text(
            msg["content"],
            font_size="md",
            padding="1rem",
            bg=rx.cond(is_user, "blue.100", "gray.100"),
            border_radius="md",
            max_width="80%",
        ),
        align_items="flex-end" if is_user else "flex-start",
        justify_content="flex-end" if is_user else "flex-start",
        display="flex",
        margin_bottom="1rem",
    )


def index() -> rx.Component:
    """Main chat page."""
    return rx.container(
        rx.vstack(
            rx.heading("Snakky AI Chat", size="lg"),
            rx.box(
                rx.vstack(
                    rx.foreach(ChatState.messages, chat_message),
                    spacing="0.5rem",
                    height="400px",
                    overflow_y="auto",
                    border="1px solid #ccc",
                    padding="1rem",
                    border_radius="md",
                ),
                width="100%",
            ),
            rx.input(
                placeholder="Type your message...",
                value=ChatState.input_value,
                on_change=ChatState.set_input_value,
                on_blur=ChatState.send_message,
                width="100%",
                padding="0.5rem",
            ),
            rx.button(
                "Send",
                on_click=ChatState.send_message,
                is_loading=ChatState.is_loading,
                width="100%",
            ),
            spacing="1rem",
            width="100%",
            max_width="600px",
            margin="0 auto",
            padding="2rem",
        ),
        on_load=ChatState.initialize_session,
    )


app = rx.App()
app.add_page(index)
