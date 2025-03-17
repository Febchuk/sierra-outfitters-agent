# Sierra Outfitters Agent

A customer service chatbot for Sierra Outfitters, an emerging outdoor retailer competing with brands like Patagonia, Cotopaxi, and REI.

## Overview

The Sierra Outfitters Agent is an AI-powered customer service tool that helps customers with order tracking, product availability, and promotional offers. The agent maintains the Sierra Outfitters brand voice, making frequent references to the outdoors and maintaining an adventurous, helpful tone.

## Features

### 1. Order Status and Tracking
- Look up order status using customer email and order number
- Provide tracking information with links when available
- Respond with on-brand, outdoor-themed messaging

### 2. Early Risers Promotion
- Generate unique discount codes for the "Early Risers Promotion"
- Only available between 8:00-10:00 AM Pacific Time
- Provides a 10% discount code when eligible

### 3. Product Availability
- Check if products are in stock using product name or SKU
- Provide inventory levels and availability information
- Suggest alternatives when products are out of stock

## Requirements

- Python 3.8+
- OpenAI API key (for GPT-4o model)
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/sierra-outfitters-agent.git
   cd sierra-outfitters-agent
   ```

2. Create a virtual environment (recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables
   - Create a `.env.local` file in the project root directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

5. Ensure data files are present
   - Make sure the following data files exist in the `data` directory:
     - `CustomerOrders.json`
     - `ProductCatalog.json`

## Usage

To start the Sierra Outfitters Agent:

```
python sierra_outfitters_agent.py
```

This will start an interactive command-line interface where you can chat with the Sierra Outfitters Agent. Type 'exit' to end the conversation.

## Configuration

The application's configuration is stored in `config.py`. This includes:

- File paths for customer orders and product catalog
- OpenAI model settings
- Time zone settings
- Promotion settings (time window, discount percentage)
- Tracking URL templates
- Customer service contact information

You can modify these settings to customize the agent's behavior.

## Brand Voice Guidelines

The Sierra Outfitters Agent follows these brand voice guidelines:

- Makes frequent references to the outdoors
- Uses mountain emojis like 🏔️
- Uses enthusiastic phrases like "Onward into the unknown!"
- Maintains an adventurous, helpful tone
- Is concise but informative

## Logging

The application logs information to a file specified in the configuration (`sierra-outfitters-agent.log` by default). The log includes:

- Initialization events
- Customer queries
- Order status checks
- Discount code generation attempts
- Product availability checks
- Errors and exceptions

