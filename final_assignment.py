#!/usr/bin/env python3
"""
Final Assignment Solution: Conversation Management & Classification using Groq API
- Task 1: Conversation Management with Summarization
- Task 2: JSON Schema Classification & Information Extraction
"""

import json
import time
from groq import Groq

# ============================================================================
# TASK 1: CONVERSATION MANAGEMENT
# ============================================================================

class SimpleChat:
    def __init__(self, api_key, max_messages=10, max_chars=5000, max_words=1000, summarize_every=3):
        self.client = Groq(api_key=api_key)
        self.messages = []
        self.max_messages = max_messages
        self.max_chars = max_chars
        self.max_words = max_words
        self.summarize_every = summarize_every
        self.turn_count = 0
    
    def chat(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        self.turn_count += 1
        
        # Summarize if needed
        if self.turn_count % self.summarize_every == 0 and len(self.messages) > 3:
            self._summarize()
        
        # Apply truncation
        self._apply_truncation()
        
        # Get response
        response = self.client.chat.completions.create(
            messages=[{"role": "system", "content": "You are helpful."}] + self.messages,
            model="llama-3.3-70b-versatile"
        )
        
        assistant_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    
    def _summarize(self):
        if len(self.messages) < 3:
            return
        
        print(f"\n🔄 SUMMARIZING (after {self.turn_count} turns)")
        
        old_messages = self.messages[:-2]
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in old_messages])
        
        try:
            summary_response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Summarize in 2 sentences."},
                    {"role": "user", "content": f"Summarize: {conversation_text}"}
                ],
                model="llama-3.3-70b-versatile"
            )
            
            summary = summary_response.choices[0].message.content
            self.messages = [{"role": "assistant", "content": f"[SUMMARY: {summary}]"}] + self.messages[-2:]
            print(f"✅ Summarized. Now {len(self.messages)} messages")
            
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
    
    def _apply_truncation(self):
        # Message count
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
            print(f"📝 Truncated to {self.max_messages} messages")
        
        # Character count
        total_chars = sum(len(msg['content']) for msg in self.messages)
        if total_chars > self.max_chars:
            while total_chars > self.max_chars and len(self.messages) > 2:
                removed = self.messages.pop(0)
                total_chars -= len(removed['content'])
            print(f"📝 Truncated to {self.max_chars} characters")
        
        # Word count
        total_words = sum(len(msg['content'].split()) for msg in self.messages)
        if total_words > self.max_words:
            while total_words > self.max_words and len(self.messages) > 2:
                removed = self.messages.pop(0)
                total_words -= len(removed['content'].split())
            print(f"📝 Truncated to {self.max_words} words")
    
    def get_stats(self):
        total_chars = sum(len(msg['content']) for msg in self.messages)
        total_words = sum(len(msg['content'].split()) for msg in self.messages)
        return {
            "messages": len(self.messages),
            "characters": total_chars,
            "words": total_words,
            "turns": self.turn_count
        }
    
    def show_history(self):
        print(f"\n📋 HISTORY ({len(self.messages)} messages)")
        for i, msg in enumerate(self.messages, 1):
            content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"{i}. {msg['role']}: {content}")

# ============================================================================
# TASK 2: INFORMATION EXTRACTION
# ============================================================================

class InfoExtractor:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "age": {"type": ["integer", "null"]}
            }
        }
    
    def extract(self, text):
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Extract personal info. Use null for missing."},
                    {"role": "user", "content": f"Extract from: {text}"}
                ],
                model="llama-3.3-70b-versatile",
                tools=[{"type": "function", "function": {"name": "extract_info", "parameters": self.schema}}],
                tool_choice={"type": "function", "function": {"name": "extract_info"}}
            )
            
            result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            return result
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return {"name": None, "email": None, "phone": None, "location": None, "age": None}
    
    def validate(self, data):
        validation = {"is_valid": True, "errors": [], "warnings": [], "extracted_count": 0}
        
        for field, value in data.items():
            if value is not None:
                validation["extracted_count"] += 1
        
        if data.get("age") is not None:
            if not isinstance(data["age"], int):
                validation["is_valid"] = False
                validation["errors"].append("Age must be integer")
            elif data["age"] < 0 or data["age"] > 150:
                validation["warnings"].append("Age seems unrealistic")
        
        if data.get("email") and "@" not in data["email"]:
            validation["warnings"].append("Email format seems invalid")
        
        if data.get("phone"):
            phone = str(data["phone"]).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not phone.isdigit() or len(phone) < 10:
                validation["warnings"].append("Phone format seems invalid")
        
        return validation
    
    def show_results(self, text, data, validation):
        print(f"\n🔍 EXTRACTION: {text[:50]}...")
        print("Extracted Information:")
        for field, value in data.items():
            status = "✅" if value else "❌"
            display = value if value else "Not found"
            print(f"  {status} {field}: {display}")
        
        print(f"\nValidation: {validation['extracted_count']}/5 fields, {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
        if validation["errors"]:
            print(f"Errors: {', '.join(validation['errors'])}")
        if validation["warnings"]:
            print(f"Warnings: {', '.join(validation['warnings'])}")

# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_task_1():
    print("🎯 TASK 1: CONVERSATION MANAGEMENT")
    print("=" * 50)
    
    api_key = "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"
    
    # Test 1: Basic conversation
    print("\n📝 Test 1: Summarization every 3 turns (max 6 messages, 2000 chars, 500 words)")
    chat1 = SimpleChat(api_key, max_messages=6, max_chars=2000, max_words=500, summarize_every=3)
    
    topics = [
        "Hi! I'm working on a Python project.",
        "I need help with data structures.",
        "What's the best way to store user data?",
        "Should I use a database or files?",
        "What about SQLite vs PostgreSQL?",
        "How do I connect to a database?",
        "Can you show me code examples?",
        "What about error handling?"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\nTurn {i}: {topic}")
        response = chat1.chat(topic)
        print(f"Response: {response[:80]}...")
        stats = chat1.get_stats()
        print(f"Stats: {stats['messages']} msgs, {stats['characters']} chars, {stats['words']} words")
    
    chat1.show_history()
    
    # Test 2: Different settings
    print(f"\n📝 Test 2: Different settings (max 4 messages, 1000 chars, 200 words)")
    chat2 = SimpleChat(api_key, max_messages=4, max_chars=1000, max_words=200, summarize_every=2)
    
    short_topics = [
        "Hello! I need help with machine learning.",
        "What's the difference between supervised and unsupervised learning?",
        "Can you explain neural networks?",
        "How do I implement a simple neural network?",
        "What about deep learning frameworks?"
    ]
    
    for i, topic in enumerate(short_topics, 1):
        print(f"\nTurn {i}: {topic}")
        response = chat2.chat(topic)
        print(f"Response: {response[:60]}...")
        stats = chat2.get_stats()
        print(f"Stats: {stats['messages']} msgs, {stats['characters']} chars, {stats['words']} words")

def demo_task_2():
    print("\n\n🎯 TASK 2: INFORMATION EXTRACTION")
    print("=" * 50)
    
    api_key = "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"
    extractor = InfoExtractor(api_key)
    
    test_cases = [
        "Hi, I'm John Smith, 28, from New York. Email: john@email.com, Phone: (555) 123-4567",
        "Hello! My name is Sarah. I'm 35 and live in California. Contact: sarah@company.com",
        "Hey, I'm Mike from Seattle. You can reach me at mike@tech.io",
        "I need help with my coding project. Can you assist me?"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}: {text}")
        data = extractor.extract(text)
        validation = extractor.validate(data)
        extractor.show_results(text, data, validation)
        time.sleep(1)

def demo_combined():
    print("\n\n🎯 COMBINED WORKFLOW")
    print("=" * 50)
    
    api_key = "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"
    
    chat = SimpleChat(api_key, max_messages=5, max_chars=1500, max_words=300, summarize_every=4)
    extractor = InfoExtractor(api_key)
    
    conversation = [
        "Hi, I'm calling about my account. I'm David Chen, 34, from Vancouver.",
        "My email is david@email.com and phone is 604-555-0198.",
        "I'm having trouble with my subscription billing.",
        "Can you help me understand why I was charged twice?",
        "I'd like to speak to a manager about this issue."
    ]
    
    full_text = ""
    for i, msg in enumerate(conversation, 1):
        print(f"\nTurn {i}: {msg}")
        full_text += f"Customer: {msg}\n"
        
        response = chat.chat(msg)
        print(f"Agent: {response[:60]}...")
        full_text += f"Agent: {response}\n"
        
        stats = chat.get_stats()
        print(f"History: {stats['messages']} msgs, {stats['characters']} chars, {stats['words']} words")
    
    print(f"\n🔍 EXTRACTING CUSTOMER INFO")
    customer_info = extractor.extract(full_text)
    validation = extractor.validate(customer_info)
    extractor.show_results(full_text, customer_info, validation)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🚀 FINAL GROQ API ASSIGNMENT")
    print("Conversation Management & Classification")
    print("=" * 60)
    
    try:
        demo_task_1()
        demo_task_2()
        demo_combined()
        print(f"\n\n✅ ALL DEMONSTRATIONS COMPLETED!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your API key and quota.")
