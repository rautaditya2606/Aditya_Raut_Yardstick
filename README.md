<<<<<<< HEAD
# Groq API Assignment: Conversation Management & Classification

This project implements two core tasks using Groq APIs with OpenAI compatibility for conversation management and information extraction.

## Overview

The solution demonstrates advanced conversation handling with automatic summarization and structured data extraction from chat conversations. It uses Groq's fast language models to provide real-time conversation management and intelligent information classification.

## Features

### Task 1: Conversation Management with Summarization

The conversation manager maintains a running history of user-assistant interactions and automatically summarizes conversations to prevent memory overflow. Key features include:

- **Automatic Summarization**: Summarizes conversations after every k turns to keep history manageable
- **Multiple Truncation Options**: Limits conversation by message count, character count, and word count
- **Smart History Management**: Preserves recent context while replacing old messages with summaries
- **Real-time Statistics**: Tracks message count, character count, and word count

### Task 2: JSON Schema Classification & Information Extraction

The information extractor uses OpenAI function calling with Groq API to extract structured data from conversations. It can identify and extract:

- **Personal Information**: Name, email, phone number, location, and age
- **Schema Validation**: Validates extracted data against predefined JSON schema
- **Error Handling**: Gracefully handles missing or invalid information
- **Format Validation**: Basic validation for email and phone number formats

## Installation

1. Install the required dependency:
```bash
pip install groq
```

2. Update the API key in the code:
```python
api_key = "your_groq_api_key_here"
```

## Usage

### Basic Conversation Management

```python
from final_assignment import SimpleChat

# Create chat instance with custom settings
chat = SimpleChat(
    api_key="your_api_key",
    max_messages=10,      # Keep last 10 messages
    max_chars=5000,       # Limit to 5000 characters
    max_words=1000,       # Limit to 1000 words
    summarize_every=3     # Summarize every 3 turns
)

# Chat with the system
response = chat.chat("Hello, I need help with Python programming")
print(response)

# Get conversation statistics
stats = chat.get_stats()
print(f"Messages: {stats['messages']}, Characters: {stats['characters']}")
```

### Information Extraction

```python
from final_assignment import InfoExtractor

# Create extractor instance
extractor = InfoExtractor("your_api_key")

# Extract information from text
text = "Hi, I'm John Smith, 28, from New York. Email: john@email.com"
data = extractor.extract(text)

# Validate extracted data
validation = extractor.validate(data)

# Display results
extractor.show_results(text, data, validation)
```

## Running the Demonstrations

The code includes three comprehensive demonstrations:

1. **Task 1 Demo**: Shows conversation management with different truncation settings
2. **Task 2 Demo**: Demonstrates information extraction from various conversation samples
3. **Combined Demo**: Shows both features working together in a customer support scenario

To run all demonstrations:

```bash
python final_assignment.py
```

## Configuration Options

### Conversation Manager Settings

- `max_messages`: Maximum number of messages to keep in history
- `max_chars`: Maximum character count for conversation
- `max_words`: Maximum word count for conversation
- `summarize_every`: Number of turns before triggering summarization

### Information Extractor Schema

The extractor looks for these five fields:
- `name`: Full name of the person
- `email`: Email address
- `phone`: Phone number
- `location`: City, state, or country
- `age`: Age in years

## Technical Details

### Dependencies

- **groq**: Groq API client for OpenAI-compatible function calling
- **json**: Standard library for JSON handling
- **time**: Standard library for rate limiting

### API Requirements

- Groq API key with sufficient quota
- Internet connection for API calls
- Python 3.7 or higher

### Rate Limiting

The code includes built-in rate limiting to prevent API quota exhaustion. It adds small delays between API calls to ensure smooth operation.

## Error Handling

The solution includes comprehensive error handling for:

- API rate limiting and quota exhaustion
- Network connectivity issues
- Invalid API responses
- Malformed data extraction

## Assignment Requirements Met

This implementation satisfies all assignment requirements:

- Uses only Python standard library and Groq client (no frameworks)
- Implements OpenAI-compatible function calling
- Provides conversation management with summarization
- Includes JSON schema classification and extraction
- Demonstrates multiple test cases and validation
- Ready for Google Colab submission

## File Structure

```
Aditya_Raut_Yardstick.ipynb    # Main solution file
README.md                      # Thi s documentation
```

## Getting Started

1. Clone or download the repository
2. Install the groq package
3. Update the API key in the code
4. Run the demonstrations
5. Copy the code to Google Colab for submission
