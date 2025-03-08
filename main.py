import sqlite3
import openai

# Initialize OpenAI Client
client = openai.OpenAI(api_key="")

# Database setup
conn = sqlite3.connect("chat_memory.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (user TEXT, bot TEXT)''')
conn.commit()

def save_chat(user_input, bot_response):
    """Save conversation to the database"""
    cursor.execute("INSERT INTO chat_history (user, bot) VALUES (?, ?)", (user_input, bot_response))
    conn.commit()

def fetch_past_conversations():
    """Retrieve last 5 user-bot interactions"""
    cursor.execute("SELECT user, bot FROM chat_history ORDER BY ROWID DESC LIMIT 5")
    past_conversations = cursor.fetchall()
    return past_conversations[::-1]

def chat_with_gpt(prompt):
    """Chat with GPT while considering past memory"""
    past_chats = fetch_past_conversations()
    context = "\n".join([f"User: {u}\nBot: {b}" for u, b in past_chats])

    full_prompt = f"{context}\nUser: {prompt}\nBot: "
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}]
    ).choices[0].message.content.strip()

    save_chat(prompt, response)
    return response

if __name__ == "__main__":
    print("Chatbot Initialized! Type 'reset' to clear memory, or 'exit' to quit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "reset":
            cursor.execute("DELETE FROM chat_history")
            conn.commit()
            print("Memory reset.")
            continue
        
        response = chat_with_gpt(user_input)
        print("Chatbot:", response)
        print("--------------------------------------------------") 

        
        
        