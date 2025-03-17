"""
Sierra Outfitters Agent Configuration File
"""

# Configuration constants
CONFIG = {
    # File paths
    'CUSTOMER_ORDERS_FILE': 'data/CustomerOrders.json',
    'PRODUCT_CATALOG_FILE': 'data/ProductCatalog.json',
    'LOG_FILE': 'sierra-outfitters-agent.log',
    'ENV_FILE': '.env.local',
    
    # OpenAI settings
    'OPENAI_MODEL': 'gpt-4o',
    
    # Time zone settings
    'TIMEZONE': 'US/Pacific',
    
    # Promotion settings
    'EARLY_RISER_START_HOUR': 8,
    'EARLY_RISER_END_HOUR': 10,
    'EARLY_RISER_DISCOUNT': '10%',
    
    # Tracking URL templates
    'USPS_TRACKING_URL': 'https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}',
    
    # Support contacts
    'CUSTOMER_SERVICE_EMAIL': 'help@sierraoutfitters.com',
}

def get_config():
    """
    Returns the configuration dictionary.
    This function allows for future enhancements like loading from JSON/YAML files.
    """
    return CONFIG
