import time
from core.agent_setup import agent

print("Content Automation System Ready\n")
print("Select an option:")
print("1: Manual Mode")
print("2: Automated Content Loop (Runs every hour)")
print("Type 'exit' to quit.\n")

def run_autopilot():
    print("\nStarting Automated Content Loop...")
    print("Press Ctrl+C to stop.\n")
    
    from core.autopilot_graph import autopilot_app
    
    while True:
        try:
            print(f"[{time.strftime('%X')}] Starting new content cycle...")
            
            # Execute the StateGraph pipeline
            final_state = autopilot_app.invoke({"recent_posts": "", "raw_news": "", "best_topic": "", "published_url": "", "status": ""})
            
            print(f"\nCycle complete. Published: {final_state.get('published_url')}\n")
            
            print(f"[{time.strftime('%X')}] Waiting for next cycle (1 hour)...")
            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping Auto-Pilot...")
            break
        except Exception as e:
            print(f"❌ Error in auto-pilot: {e}")
            time.sleep(60)

def main():
    while True:
        try:
            choice = input("Select Mode (1 or 2): ")
            if choice.lower() in ["exit", "quit", "bye"]:
                print("Agent: Goodbye! 👋")
                break
            
            if choice == "2":
                run_autopilot()
                break # After autopilot ends, loop will break
                
            elif choice == "1":
                print("\nEntering Manual Mode. Awaiting instructions.")
                print("Example: 'Fetch the latest news from Ethiopia'")
                
                # Give the agent a strict persona so it actually uses tools instead of pretending
                sys_prompt = """
                You are a research and publishing specialist.
                
                CRITICAL PROTOCOL:
                1. Before drafting or publishing any topic, you MUST call 'read_recent_topics' to check if we have already covered it.
                2. If a topic has been covered recently, INFORM the user and ask for a different topic, or suggest an alternative from the news.
                3. To answer any query about news, use the 'get_global_news' tool.
                4. Always use 'log_activity' after a successful publication.
                5. Do not hallucinate history; use 'read_recent_audit' if the user asks what you did.
                """
                chat_history = [("system", sys_prompt)]
                
                while True:
                    user_input = input("You: ")
                    if user_input.lower() in ["exit", "quit", "back"]:
                        break
                    
                    # Add user message to history
                    chat_history.append(("human", user_input))
                    
                    # Invoke agent with full history
                    response = agent.invoke({"messages": chat_history})
                    
                    # Save AI response to history so it remembers the conversation
                    ai_msg = response['messages'][-1].content
                    chat_history.append(("ai", ai_msg))
                    
                    print(f"\nAgent: {ai_msg}\n")
            else:
                print("Invalid choice. Please type 1 or 2.")
                
        except KeyboardInterrupt:
            print("\nAgent: Goodbye! 👋")
            break

if __name__ == "__main__":
    main()
