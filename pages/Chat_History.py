"""
Chat History Viewer - Interactive conversation data browser
Author: SilentCodingLegend
Version: 2.0 - Enhanced Security & Professional Features
"""
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import bleach

# --- Constants ---
CONVERSATIONS_DIR = "data/conversations"
USER_ROLE = 'user'
ASSISTANT_ROLE = 'assistant'
USER_EMOJI = "👤"
ASSISTANT_EMOJI = "🤖"

# --- Page Configuration ---
st.set_page_config(
    page_title="Chat History - SilentCodingLegend",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Utility Functions ---
def load_css(file_path: str):
    """Load a CSS file and inject it into the Streamlit app."""
    try:
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found at {file_path}. Using default styles.")

def render_metric_card(title: str, value: any, icon: str):
    """Render a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <h3>{icon} {value}</h3>
        <p>{title}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Core Application Class ---

class ChatHistoryViewer:
    """
    Manages loading, searching, and interacting with chat history data.
    """
    def __init__(self, conversations_dir: str = CONVERSATIONS_DIR):
        """
        Initializes the viewer by loading conversation data.

        Args:
            conversations_dir (str): The directory containing conversation JSON files.
        """
        self.conversations_dir = conversations_dir
        self.conversations = self.load_conversations()

    def load_conversations(self) -> Dict:
        """
        Load all conversation files securely from the specified directory.
        """
        conversations = {}
        if not os.path.exists(self.conversations_dir):
            st.error(f"Conversation directory not found: {self.conversations_dir}")
            return conversations

        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json') and filename != 'summary.json':
                filepath = os.path.join(self.conversations_dir, filename)
                
                # Security: Ensure the file path is within the intended directory
                if not os.path.abspath(filepath).startswith(os.path.abspath(self.conversations_dir)):
                    st.warning(f"Skipping potentially malicious file path: {filename}")
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    session_id = filename.replace('.json', '')
                    conversations[session_id] = {
                        'data': data,
                        'filepath': filepath,
                        'message_count': len(self._extract_messages({'data': data})),
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                    }
                except json.JSONDecodeError:
                    st.error(f"Error decoding JSON from {filename}.")
                except (IOError, OSError) as e:
                    st.error(f"Error reading file {filename}: {e}")
        return conversations

    def refresh(self):
        """Reloads the conversation data from the directory."""
        self.conversations = self.load_conversations()

    def get_session_stats(self, session_data: List[Dict]) -> Dict:
        """Get detailed statistics for a single conversation session."""
        valid_messages = [msg for msg in session_data if isinstance(msg, dict) and 'role' in msg and 'content' in msg]
        
        user_msgs = [msg for msg in valid_messages if msg['role'] == USER_ROLE]
        assistant_msgs = [msg for msg in valid_messages if msg['role'] == ASSISTANT_ROLE]
        
        total_chars = sum(len(str(msg.get('content', ''))) for msg in valid_messages)
        avg_user_len = sum(len(str(msg.get('content', ''))) for msg in user_msgs) / len(user_msgs) if user_msgs else 0
        avg_asst_len = sum(len(str(msg.get('content', ''))) for msg in assistant_msgs) / len(assistant_msgs) if assistant_msgs else 0
        
        return {
            'total_messages': len(valid_messages),
            'user_messages': len(user_msgs),
            'assistant_messages': len(assistant_msgs),
            'total_characters': total_chars,
            'avg_user_length': round(avg_user_len, 1),
            'avg_assistant_length': round(avg_asst_len, 1),
            'first_message_time': valid_messages[0].get('timestamp') if valid_messages else "N/A",
            'last_message_time': valid_messages[-1].get('timestamp') if valid_messages else "N/A"
        }

    def search_conversations(self, query: str) -> Dict:
        """Search conversations for a given query string (case-insensitive)."""
        if not query:
            return self.conversations
        
        results = {}
        query_lower = query.lower()
        
        for session_id, conv_data in self.conversations.items():
            messages = self._extract_messages(conv_data)
            matching_messages = [
                msg for msg in messages 
                if isinstance(msg, dict) and 'content' in msg and isinstance(msg.get('content'), str) 
                and query_lower in msg['content'].lower()
            ]
            
            if matching_messages:
                results[session_id] = {**conv_data, 'match_count': len(matching_messages)}
        return results

    def _extract_messages(self, conv_data: Dict) -> List[Dict]:
        """Extracts the list of messages from potentially varied data structures."""
        messages_data = conv_data.get('data', [])
        if isinstance(messages_data, dict) and 'messages' in messages_data:
            return messages_data['messages']
        elif isinstance(messages_data, list):
            return messages_data
        return []

    def export_conversation(self, session_id: str, format_type: str = "markdown") -> str:
        """Exports a conversation to the specified format (Markdown, JSON, or TXT)."""
        messages = self._extract_messages(self.conversations[session_id])
        
        if format_type == "markdown":
            content = f"# Conversation: {session_id}\n\n"
            for msg in messages:
                role_emoji = USER_EMOJI if msg.get('role') == USER_ROLE else ASSISTANT_EMOJI
                content += f"## {role_emoji} {msg.get('role', 'unknown').title()}\n"
                content += f"**Time:** {msg.get('timestamp', 'N/A')}\n\n"
                content += f"{msg.get('content', '[No Content]')}\n\n---\n\n"
            return content
        
        elif format_type == "json":
            return json.dumps(messages, indent=2, ensure_ascii=False)
        
        elif format_type == "txt":
            content = f"CONVERSATION EXPORT: {session_id}\n{'='*50}\n\n"
            for msg in messages:
                content += f"[{msg.get('timestamp', 'N/A')}] {msg.get('role', 'unknown').upper()}: {msg.get('content', '[No Content]')}\n\n"
            return content
        
        return "Invalid export format selected."

    def delete_conversation(self, session_id: str) -> bool:
        """Deletes a conversation file from the disk."""
        if session_id not in self.conversations:
            st.error("Session ID not found.")
            return False
        
        filepath = self.conversations[session_id]['filepath']
        try:
            os.remove(filepath)
            del self.conversations[session_id]
            return True
        except FileNotFoundError:
            st.error(f"File not found for deletion: {filepath}")
        except OSError as e:
            st.error(f"Error deleting conversation file: {e}")
        return False

# --- Main Application Logic ---
def main():
    """Main function to run the Streamlit application."""
    load_css("assets/chat_history_styles.css")
    
    st.markdown('<h1 class="main-header">📚 Chat History Browser</h1>', unsafe_allow_html=True)

    # Initialize or retrieve the viewer from session state
    if 'viewer' not in st.session_state:
        st.session_state.viewer = ChatHistoryViewer()
    
    viewer = st.session_state.viewer

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("## 📚 Chat History")
        st.markdown("**Interactive Conversation Browser**")
        
        if st.button("🔄 Refresh Data"):
            viewer.refresh()
            st.success("Data refreshed!")
            st.rerun()

        st.markdown("### 🔍 Search")
        search_query = st.text_input("Search conversations:", placeholder="Enter keywords...")

        st.markdown("### 👀 View Options")
        show_timestamps = st.checkbox("Show timestamps", value=True)
        show_metadata = st.checkbox("Show metadata", value=False)
        messages_per_page = st.selectbox("Messages per page:", [10, 25, 50, 100], index=1)

    # --- Main Content ---
    if not viewer.conversations:
        st.warning(f"No conversation history found in the `{CONVERSATIONS_DIR}` directory.")
        return

    # Apply search and get conversations to display
    conversations_to_show = viewer.search_conversations(search_query)
    
    if search_query:
        if conversations_to_show:
            st.success(f"Found {len(conversations_to_show)} conversations matching '{search_query}'.")
        else:
            st.warning(f"No conversations found for '{search_query}'.")
            return
            
    # --- Overall Statistics ---
    st.markdown("## 📊 Overall Statistics")
    total_convs = len(conversations_to_show)
    total_msgs = sum(conv['message_count'] for conv in conversations_to_show.values())
    avg_msgs = total_msgs / total_convs if total_convs > 0 else 0
    latest_date = max(conv['last_modified'] for conv in conversations_to_show.values()) if conversations_to_show else datetime.now()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Conversations", total_convs, "📁")
    with col2:
        render_metric_card("Total Messages", total_msgs, "💬")
    with col3:
        render_metric_card("Avg Msgs/Conv", f"{avg_msgs:.1f}", "📈")
    with col4:
        render_metric_card("Latest Activity", latest_date.strftime('%b %d, %Y'), "📅")

    # --- Conversation Browser ---
    st.markdown("---")
    st.markdown("## 💬 Conversation Explorer")
    
    session_options = {
        sid: f"{sid} ({c['message_count']} msgs - {c['last_modified'].strftime('%Y-%m-%d %H:%M')})"
        for sid, c in conversations_to_show.items()
    }
    
    selected_session_id = st.selectbox(
        "Select a conversation to view:",
        options=list(session_options.keys()),
        format_func=lambda sid: session_options[sid]
    )
    
    if not selected_session_id:
        return

    selected_conv = conversations_to_show[selected_session_id]
    session_stats = viewer.get_session_stats(viewer._extract_messages(selected_conv))

    # --- Session Details and Actions ---
    with st.expander("📋 Session Details & Actions", expanded=True):
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown(f"""
            - **ID:** `{selected_session_id}`
            - **Messages:** `{session_stats['user_messages']}` user, `{session_stats['assistant_messages']}` assistant
            - **Total Characters:** `{session_stats['total_characters']:,}`
            - **Avg User Msg Length:** `{session_stats['avg_user_length']}` chars
            - **Avg Assistant Msg Length:** `{session_stats['avg_assistant_length']}` chars
            """)

        with col2:
            export_format = st.selectbox("Export Format:", ["markdown", "json", "txt"], key="export_format")
            exported_content = viewer.export_conversation(selected_session_id, export_format)
            st.download_button(
                label=f"📥 Download .{export_format}",
                data=exported_content,
                file_name=f"{selected_session_id}.{export_format}",
                mime=f"text/{export_format}"
            )
            if st.button("🗑️ Delete Conversation", use_container_width=True):
                if viewer.delete_conversation(selected_session_id):
                    st.success(f"Conversation '{selected_session_id}' has been deleted.")
                    st.rerun()

    # --- Message Display with Pagination ---
    st.markdown("### Messages")
    messages_data = viewer._extract_messages(selected_conv)
    total_messages = len(messages_data)
    
    if total_messages > messages_per_page:
        total_pages = (total_messages - 1) // messages_per_page + 1
        page_num = st.number_input("Page", 1, total_pages, 1)
        start_idx = (page_num - 1) * messages_per_page
        end_idx = min(start_idx + messages_per_page, total_messages)
        messages_to_show = messages_data[start_idx:end_idx]
        st.info(f"Showing messages {start_idx + 1}-{end_idx} of {total_messages}")
    else:
        messages_to_show = messages_data

    for message in messages_to_show:
        role = message.get('role', 'unknown')
        # Security: Sanitize content before rendering
        content = bleach.clean(message.get('content', '[No Content]'))
        
        message_class = "user-message" if role == USER_ROLE else "assistant-message"
        role_emoji = USER_EMOJI if role == USER_ROLE else ASSISTANT_EMOJI
        
        with st.container():
            st.markdown(f'<div class="chat-message {message_class}">', unsafe_allow_html=True)
            st.markdown(f"**{role_emoji} {role.title()}**", unsafe_allow_html=True)
            if show_timestamps and 'timestamp' in message:
                st.caption(f"🕒 {message['timestamp']}")
            st.markdown(content) # Render sanitized content
            if show_metadata and 'metadata' in message:
                st.json(message['metadata'], expanded=False)
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
