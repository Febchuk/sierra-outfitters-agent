from openai import OpenAI
import os
from dotenv import load_dotenv
import pytz
import json
from typing import Dict, Any, List
import uuid
from colorama import Fore, Style
from datetime import datetime
import logging
from config import get_config

# Import configuration from config.py
CONFIG = get_config()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(CONFIG['LOG_FILE'])
    ]
)

logger = logging.getLogger(__name__)

class SierraOutfittersAgent:
    """ Main class for the Sierra Outfitters Agent """

    def __init__(self, api_key):
        """ Initialize the Sierra Outfitters Agent """
        logger.info("Initializing Sierra Outfitters Agent")
        self.client = OpenAI(api_key=api_key)
        self.pacific_tz = pytz.timezone(CONFIG['TIMEZONE'])
        self.orders_data = []
        self.products_data = []
        self.conversation_history = []
        self.load_data()
        self.setup_system_prompt()
        self.tools = self.define_tools()
        logger.info("Agent initialization complete")

    def load_data(self):
        """ Load data from JSON files """
        logger.info("Loading data from JSON files")
        try:
            with open(CONFIG['CUSTOMER_ORDERS_FILE'], 'r') as f:
                self.orders_data = json.load(f)
                logger.info(f"Loaded {len(self.orders_data)} customer orders")
            with open(CONFIG['PRODUCT_CATALOG_FILE'], 'r') as f:
                self.products_data = json.load(f)
                logger.info(f"Loaded {len(self.products_data)} products")

        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            print("Data files not found. Please ensure the data files exist.")

    def setup_system_prompt(self):
        """Setup the system prompt for the chatbot"""
        logger.debug("Setting up system prompt")
        self.system_prompt = """
        You are the customer service agent for Sierra Outfitters, an emerging outdoor retailer competing with Patagonia, Cotopaxi, and REI.

        Brand Voice Guidelines:
        - Make frequent references to the outdoors
        - Use outdoor emojis like 🏔️ and more
        - Use enthusiastic phrases like "Onward into the unknown!" and more
        - Maintain an adventurous, helpful tone
        - Be concise but informative

        Here are your capabilities:
        1. Order Status and Tracking: You can look up order status by asking for the customer's email and order number.
        - If they only provide one piece of information, remember it and ask for the other piece.
        - Once you have both email and order number, look up the order status.

        2. Early Risers Promotion: Between 8:00-10:00 AM Pacific Time, offer a 10% discount code when customers ask for the "Early Risers Promotion". Check if we can generate a discount code. If not politely decline.

        3. Product Availability: You can check product availability for customers.
        - Customers will typically search by product name rather than SKU or technical details.
        - Prioritize matching products by name over SKU or tags when a customer asks about a product.
        - When using the check_product_availability function, try to extract the most likely product name from the customer's query.

        Guardrails:
        - You can only provide information about the products in the catalog
        - If you don't have the answer, say you don't know instead of making it up
        - You can only offer the Early Risers Promotion between 8:00-10:00 AM Pacific Time. Otherwise you must politely decline and suggest come back at valid time.

        When you receive a function response with a "formatted_response" field:
        - Use this as inspiration rather than repeating it verbatim
        - Maintain the same factual information (order status, inventory levels, etc.)
        - Keep the Sierra Outfitters brand voice (mountain references, outdoor enthusiasm, emojis)
        - Vary your phrasing naturally to avoid repetitive interactions with the same customer

        Example transformation:

        Formatted response: 
        "Great news, John! Your order #W001 has reached its destination. Your adventure gear is ready to use! 🏔️"

        Better, more natural response:
        "Summit success, John! I just checked and your order #W001 has made it to your basecamp. Your new gear is ready for whatever adventure awaits! Time to hit the trails! 🏔️"

        Formatted response:
        "Good news, trail-seeker! The Wilderness Backpack (SKU: SOSV001) is available, but only 3 left in stock! These are going faster than a downhill trail run! 🏔️"

        Better, more natural response: 
        "I've scouted ahead and found good news! We still have 3 Wilderness Backpacks (SKU: SOSV001) waiting for their next adventure. They're practically strapping themselves on and heading out the door though, so I wouldn't wait too long! 🏔️"

        The goal is to sound like a helpful, enthusiastic outdoor guide with diverse language while delivering consistent information.
        """

    def define_tools(self):
        """ Define the tools available to the chatbot """
        logger.debug("Defining agent tools")
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_order_status",
                    "description": "Check the status of an order by email and order number. Use this when a customer wants to know about their order status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Customer's email address associated with the order"},
                            "order_number": {"type": "string", "description": "Order number, with or without the # prefix"}
                        },
                        "required": ["email", "order_number"]
                    },
                    "return": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "customer_name": {"type": "string"},
                            "status": {"type": "string"},
                            "tracking_info": {"type": "string"},
                            "formatted_response": {"type": "string", "description": "A complete, ready-to-present response with the Sierra Outfitters voice"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_discount_code",
                    "description": "Generate a unique discount code for Early Risers Promotion. Only available between 8:00-10:00 AM Pacific Time.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    },
                    "return": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "discount_code": {"type": "string"},
                            "formatted_response": {"type": "string", "description": "A complete, ready-to-present response with the Sierra Outfitters voice"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_product_availability",
                    "description": "Check product availability by SKU or Product Name. Use this when a customer asks about a specific product.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_query": {"type": "string", "description": "Product SKU, name, or a descriptive term that might match product tags"}
                        },
                        "required": ["product_query"]
                    },
                    "return": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "product_name": {"type": "string"},
                            "sku": {"type": "string"},
                            "in_stock": {"type": "boolean"},
                            "inventory": {"type": "integer"},
                            "formatted_response": {"type": "string", "description": "A complete, ready-to-present response with the Sierra Outfitters voice"}
                        }
                    }
                }
            }
        ]

    # ======== Feature 1: Order Status and Tracking ========
    
    def check_order_status(self, email: str, order_number: str) -> Dict[str, Any]:
        """ Check the status of an order by email and order number 
        
        Returns:
            Dict with the following structure:
            {
                "success": bool,  # Whether the order was found
                "customer_name": str,  # Name of the customer (if found)
                "status": str,  # Status of the order (if found)
                "tracking_info": str,  # Tracking information (if available)
                "formatted_response": str  # A properly formatted customer-facing response
            }
        """

        logger.info(f"Checking order status for email: {email}, order: {order_number}")
        # If order_number doesn't have a # prefix, add it
        if order_number and not order_number.startswith("#"):
            order_number = "#" + order_number
            
        order = next((order for order in self.orders_data 
        if order['Email'].lower() == email.lower() 
        and order['OrderNumber'].lower() == order_number.lower()
        ), None)

        if not order:
            logger.warning(f"Order not found for email: {email}, order: {order_number}")
            return {
                "success": False,
                "formatted_response": "We couldn't find your order. Please check your email and order number and try again. The mountain path is clearer with the right coordinates! 🏔️"
            }

        # Generate tracking info if available
        tracking_info = ""
        if order['TrackingNumber']:
            tracking_url = CONFIG['USPS_TRACKING_URL'].format(tracking_number=order['TrackingNumber'])
            tracking_info = f"You can track your order at {tracking_url}."
            logger.debug(f"Generated tracking URL for order {order_number}: {tracking_url}")

        # Format status messages with outdoorsy messages
        status_messages = {
            "delivered": f"Great news, {order['CustomerName']}! Your order {order['OrderNumber']} has reached its destination. Your adventure gear is ready to use! 🏔️",
            "in-transit": f"Hi {order['CustomerName']}! Your order {order['OrderNumber']} is on the move - like a hiker on a mission! {tracking_info} The peaks are waiting! 🏔️",
            "fulfilled": f"Hello {order['CustomerName']}! Your order {order['OrderNumber']} has been packed and is ready to begin its journey! Onward into the unknown! 🏔️",
            "error": f"There seems to be a boulder in the path of your order {order['OrderNumber']}, {order['CustomerName']}. Please contact our customer service at {CONFIG['CUSTOMER_SERVICE_EMAIL']}. We're here to help you navigate the trail! 🏔️"
        }

        formatted_response = status_messages.get(
            order['Status'], 
            f"Hi {order['CustomerName']}! Your order {order['OrderNumber']} is being processed. The adventure awaits! 🏔️"
        )

        logger.info(f"Order found for {email}, status: {order['Status']}")
        return {
            "success": True,
            "customer_name": order["CustomerName"],
            "status": order['Status'],
            "tracking_info": tracking_info if order['TrackingNumber'] else "No tracking information yet, but your adventure is coming soon! 🏔️",
            "formatted_response": formatted_response
        }

    # ======== Feature 2: Early Risers Promotion ========

    def check_early_riser_eligibility(self) -> bool:
        """ Check if it's time for the Early Risers Promotion """

        logger.debug("Checking Early Risers Promotion eligibility")
        now = datetime.now(self.pacific_tz)
        start_time = now.replace(hour=CONFIG['EARLY_RISER_START_HOUR'], minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=CONFIG['EARLY_RISER_END_HOUR'], minute=0, second=0, microsecond=0)

        # Check if it's between 8:00 and 10:00 AM Pacific Time
        is_eligible = start_time <= now < end_time
        logger.info(f"Early Risers eligibility: {is_eligible}, current time (PT): {now.strftime('%H:%M:%S')}")
        return is_eligible

    def generate_discount_code(self) -> Dict[str, Any]:
        """ Generate a unique discount code for Early Risers Promotion 
        
        Returns:
            Dict with the following structure:
            {
                "success": bool,  # Whether a discount code was generated
                "discount_code": str,  # The generated discount code (if successful)
                "formatted_response": str  # A properly formatted customer-facing response
            }
        """
        
        if not self.check_early_riser_eligibility():
            logger.info("Early Risers Promotion requested outside of eligible hours")
            return {
                "success": False,
                "formatted_response": f"The Early Risers Promotion is only available between {CONFIG['EARLY_RISER_START_HOUR']}:00-{CONFIG['EARLY_RISER_END_HOUR']}:00 AM Pacific Time. It's currently {datetime.now(self.pacific_tz).strftime('%I:%M %p')} Pacific Time. Come back during our promotion hours to claim your discount! The mountains will be waiting! 🏔️"
            }

        # Generate a unique discount code
        unique_id = str(uuid.uuid4())[:8].upper()
        discount_code = f"EARLY10-{unique_id}"
        logger.info(f"Generated Early Risers discount code: {discount_code}")

        return {
            "success": True,
            "discount_code": discount_code,
            "formatted_response": f"You've earned an Early Risers discount! Use code {discount_code} for {CONFIG['EARLY_RISER_DISCOUNT']} off your next purchase. The early explorer catches the best views! 🏔️"
        }
    
    # ======== Feature 3: Product Availability ========

    def check_product_availability(self, product_query: str) -> Dict[str, Any]:
        """Check if a product is available in the inventory
        
        Returns:
            Dict with the following structure:
            {
                "success": bool,  # Whether the product was found
                "product_name": str,  # Name of the product (if found)
                "sku": str,  # SKU of the product (if found)
                "in_stock": bool,  # Whether the product is in stock (if found)
                "inventory": int,  # Quantity available (if found)
                "formatted_response": str  # A properly formatted customer-facing response
            }
        """

        logger.info(f"Checking product availability for query: '{product_query}'")

        # First, try to find an exact match by SKU
        product = next((p for p in self.products_data if p["SKU"].lower() == product_query.lower()), None)
        
        # If no exact SKU match, try finding by name (partial match)
        if not product:
            matching_products = [p for p in self.products_data 
                                if product_query.lower() in p["ProductName"].lower()]
            
            # If still no match, try matching by tags
            if not matching_products:
                matching_products = [p for p in self.products_data 
                                    if any(product_query.lower() in tag.lower() for tag in p["Tags"])]
            
            # If we found multiple products, just take the first one for simplicity
            product = matching_products[0] if matching_products else None
        
        if not product:
            logger.warning(f"No product found matching query: '{product_query}'")
            return {
                "success": False,
                "formatted_response": "I couldn't find that product in our catalog. Can you try a different name or description? Every explorer needs the right gear for their journey! 🏔️"
            }
        
        # Check inventory
        in_stock = product["Inventory"] > 0
        logger.info(f"Product found: {product['ProductName']}, SKU: {product['SKU']}, In Stock: {in_stock}, Quantity: {product['Inventory']}")
        
        # Format the response based on inventory status
        if in_stock:
            if product["Inventory"] < 10:
                formatted_response = f"Good news, trail-seeker! The {product['ProductName']} (SKU: {product['SKU']}) is available, but only {product['Inventory']} left in stock! These are going faster than a downhill trail run! 🏔️"
            else:
                formatted_response = f"Great choice! The {product['ProductName']} (SKU: {product['SKU']}) is well-stocked with {product['Inventory']} available. Ready for your next adventure! 🏔️"
        else:
            formatted_response = f"I'm sorry, the {product['ProductName']} (SKU: {product['SKU']}) is currently out of stock. Even the best trails need maintenance sometimes. Check back soon or explore our other adventure gear! 🏔️"
        
        return {
            "success": True,
            "product_name": product["ProductName"],
            "sku": product["SKU"],
            "in_stock": in_stock,
            "inventory": product["Inventory"],
            "formatted_response": formatted_response
        }

    # ======== Main Agent Helper Functions ========

    def _add_to_conversation_history(self, role: str, content: any):
        """Add a message to the conversation history"""
        if role == "user" or role == "assistant" or role == "system":
            # For standard message types
            self.conversation_history.append({"role": role, "content": content})
        elif role == "model_dump" or role == "function_response":
            # For function responses
            self.conversation_history.append(content)
        else:
            logger.warning(f"Unexpected role type in _add_to_conversation_history: {type(role)}")

    def _get_initial_model_response(self):
        """Get the initial response from the LLM"""
        logger.debug("Calling OpenAI API")
        
        # Construct messages array with system prompt and full conversation history
        messages = [
            {"role": "system", "content": self.system_prompt},
        ] + self.conversation_history
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=CONFIG['OPENAI_MODEL'],
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        logger.debug("Received response from OpenAI API")
        return response.choices[0].message

    def _process_tool_calls(self, message):
        """Process tool calls from the model's response"""
        logger.info(f"Tool calls detected: {len(message.tool_calls)}")
        
        # Add the assistant's tool calls to conversation history
        self._add_to_conversation_history("model_dump", message.model_dump())
        
        # Execute tool calls and collect responses
        function_responses = self._execute_tool_calls(message.tool_calls)
        
        # Add function responses to conversation history
        for func_response in function_responses:
            self._add_to_conversation_history("function_response", func_response)
        
        # Get final response incorporating tool results
        return self._get_final_response_with_tools()

    def _execute_tool_calls(self, tool_calls):
        """Execute the tool calls and return the responses"""
        function_responses = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            logger.info(f"Executing tool call: {function_name}")
            logger.debug(f"Tool call arguments: {function_args}")
            
            try:
                function_response = self._call_tool_function(function_name, function_args)
                
                # Validate the response
                if function_response and "formatted_response" in function_response:
                    if function_response.get("success", False):
                        logger.debug(f"Tool call successful: {function_name}")
            except Exception as e:
                logger.error(f"Error executing tool call {function_name}: {str(e)}")
                function_response = {
                    "success": False,
                    "error": str(e),
                    "formatted_response": "Sorry, I encountered an issue while processing your request. The trail got a bit rocky there! Can you try again? 🏔️"
                }
            
            function_responses.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })
        
        return function_responses

    def _call_tool_function(self, function_name, function_args):
        """Call the appropriate tool function based on the function name"""
        if function_name == "check_order_status":
            return self.check_order_status(
                function_args.get("email", ""),
                function_args.get("order_number", "")
            )
        elif function_name == "generate_discount_code":
            return self.generate_discount_code()
        elif function_name == "check_product_availability":
            return self.check_product_availability(
                function_args.get("product_query", "")
            )
        else:
            logger.warning(f"Unknown function called: {function_name}")
            return {
                "success": False,
                "error": f"Unknown function: {function_name}",
                "formatted_response": "I don't know how to do that yet. But I'm always learning new trails! 🏔️"
            }

    def _get_final_response_with_tools(self):
        """Get the final response from the model after tool calls"""
        try:
            logger.debug("Calling OpenAI API for final response")
            final_response = self.client.chat.completions.create(
                model=CONFIG['OPENAI_MODEL'],
                messages=[
                    {"role": "system", "content": self.system_prompt}
                ] + self.conversation_history,
                tools=self.tools,
                tool_choice="auto"
            )
            logger.debug("Received final response from OpenAI API")
        except Exception as e:
            logger.error(f"Error calling OpenAI API for final response: {str(e)}")
            return "I'm sorry, I encountered an issue connecting to my base camp. Can you try again in a moment? 🏔️"

        # Extract message from final response
        final_message = final_response.choices[0].message
        
        # Add final assistant response to conversation history
        self._add_to_conversation_history("assistant", final_message.content)
        logger.info("Final response generated successfully")
        
        return final_message.content

    def _process_direct_response(self, message):
        """Handle a direct response with no tool calls"""
        logger.info("No tool calls detected, returning direct response")
        response_content = message.content
        self._add_to_conversation_history("assistant", response_content)
        return response_content

    # ======== Main Agent Function Call ========

    def process_message(self, user_message: str) -> str:
        """ Process a message and return a response """
        
        logger.info(f"Processing user message: '{user_message[:50]}...' (truncated)")
        
        # Update conversation with user message
        self._add_to_conversation_history("user", user_message)
        
        # Get initial model response
        try:
            message = self._get_initial_model_response()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return "I'm sorry, I encountered an issue connecting to my base camp. Can you try again in a moment? 🏔️"

        # Handle tool calls if present
        if message.tool_calls:
            return self._process_tool_calls(message)
        
        # Handle direct response
        return self._process_direct_response(message)

    def run_chat_loop(self):
        """ Run the main chat loop."""
        logger.info("Starting chat loop")
        print(f"{Fore.GREEN}🏔️ Sierra Outfitters Assistant{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Type 'exit' to end the conversation{Style.RESET_ALL}")

        # Initial greeting
        initial_response = "🏔️ Welcome to Sierra Outfitters! How can I help you today? Onward into the unknown!"
        print(f"\n{Fore.GREEN}Sierra: {Style.RESET_ALL}{initial_response}\n")
        
        # Add initial greeting to conversation history
        self.conversation_history.append({"role": "assistant", "content": initial_response})
  
        while True:
            user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
            if user_input.lower() == 'exit':
                logger.info("User requested exit, ending chat loop")
                print(f"\n{Fore.GREEN}Sierra: {Style.RESET_ALL}Goodbye! Have a safe and adventurous journey! 🏔️\n")
                break
            
            try:
                response = self.process_message(user_input)
                print(f"\n{Fore.GREEN}Sierra: {Style.RESET_ALL}{response}\n")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                print(f"\n{Fore.GREEN}Sierra: {Style.RESET_ALL}I'm sorry, something went wrong on our hiking trail. Please try again! 🏔️\n")

def main():
    """ Main function to run the Sierra Outfitters Agent """
    try:
        logger.info("Starting Sierra Outfitters Agent")
        
        # Load environment variables
        load_dotenv(CONFIG['ENV_FILE'])
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("Missing OpenAI API key. Please set the OPENAI_API_KEY environment variable.")
            print("Missing OpenAI API key. Please set the OPENAI_API_KEY environment variable.")
            return
        
        agent = SierraOutfittersAgent(api_key)
        agent.run_chat_loop()
    except KeyboardInterrupt:
        logger.info("Agent terminated by keyboard interrupt")
        print("\nExiting Sierra Agent. Happy trails! 🏔️")
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}", exc_info=True)
        print(f"Failed to run chat loop: {str(e)}")
        return
    finally:
        logger.info("Sierra Outfitters Agent shutdown complete")

if __name__ == "__main__":
    main()