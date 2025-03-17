# Agent Loop Exercise Summary Report

## Testing and Reliability

How would you test for regressions as a customer requests new changes? What monitoring and alerting would you like available?

### Unit Testing
- **Order Status Function**: Test with various combinations of valid/invalid emails and order numbers
  - Valid email + valid order number → Returns correct order details
  - Valid email + invalid order number → Returns appropriate error
  - Invalid email + valid order number → Returns appropriate error
  - Edge cases: Orders with null tracking numbers, orders in each status state

- **Early Risers Promotion**: 
  - Mock system time to 8:30 AM PT → Discount code generated successfully
  - Mock system time to 10:15 AM PT → Polite rejection message
  - Test uniqueness of generated codes across multiple calls

- **Product Availability**:
  - Test exact SKU matches (e.g., "SOSV001")
  - Test partial name matches (e.g., "Backpack")
  - Test tag-based matches (e.g., "Hiking")
  - Test products with varying inventory levels (in stock, low stock, out of stock)
  - Test with nonexistent products

### Integration Testing
- **Conversation State Persistence**: Verify that the agent remembers previous information in multi-turn conversations
  - Customer provides email → Agent asks for order number → Agent successfully retrieves order
  - Customer asks about backpack → Agent responds about backpack availability → Customer asks "how many are left?" → Agent correctly references the previously identified product

- **Tool Selection Logic**: Ensure the agent selects the right function for ambiguous queries
  - "Where's my order?" → Should trigger order status flow, not product availability
  - "Do you have Ishmeet's Jetpack?" → Should trigger product availability, not order status

### Regression Test Suite
- Create a regression test suite with 20-30 conversation flows covering all features
- Automate testing with scripts that simulate user inputs and validate agent responses
- Run regression tests on every code push and before each deployment

### Monitoring Specifics
- **Error Rate Monitoring**: Alert if error rate exceeds 5% for any function over a 10-minute window
- **Response Time Monitoring**: Alert if average response time exceeds 3 seconds
- **Conversation Length Monitoring**: Flag if conversations exceed a certain number of turns
- **LLM Cost Monitoring**: Track token usage and alert on abnormal spikes

## Evaluation and Customer Success

How would you measure success for an AI agent? What metrics would give customers visibility to the quality of the AI agent?

### Core Success Metrics

1. **Resolution Rate & Accuracy**
   - **First Contact Resolution (FCR)**: Percentage of customer inquiries resolved in the first interaction (target: >75%)
   - **Overall Resolution Rate**: Percentage of inquiries resolved without human escalation (target: >90%)
   - **Accuracy of Information**: Correctness of order status, product details, and other factual information (measured through sampling and review)
   - **Error Tracking**: Rate of detected factual errors or hallucinations per 100 conversations

2. **Task Completion Metrics**
   - **Order Status Success Rate**: Percentage of order lookups that successfully return accurate status information 
   - **Product Availability Success Rate**: Accuracy in identifying correct products when customers use descriptive language rather than exact names
   - **Early Risers Promotion Compliance**: Percentage of discount code requests properly handled according to time-of-day rules
   - **Task Abandonment Rate**: Percentage of conversations where customers give up before completing their intended task

3. **Conversation Quality Metrics**
   - **Average Conversation Length**: Number of turns to complete common tasks (with benchmarks for each task type)
   - **Response Relevance Score**: Evaluation of whether agent responses directly address customer queries (using NLP techniques)
   - **Contextual Understanding**: Measurement of agent's ability to maintain context across a multi-turn conversation
   - **Brand Voice Consistency**: Automated scoring of brand voice elements (outdoor references, proper emoji usage, enthusiastic phrasing)
   - **Sentiment Progression**: Tracking how customer sentiment evolves throughout conversations

4. **Customer Experience Metrics**
   - **CSAT (Customer Satisfaction)**: Post-conversation ratings (1-5 scale)
   - **CES (Customer Effort Score)**: How easy was it for customers to get their needs met (1-7 scale)
   - **NPS (Net Promoter Score)**: Likelihood to recommend Sierra Outfitters based on AI interaction
   - **Customer Feedback Analysis**: Thematic categorization of free-text feedback
   - **Repeat Usage**: Rate at which customers return to use the agent for additional inquiries

### Advanced Analytics

1. **Conversation Flow Analysis**
   - Visual flowcharts of common conversation paths
   - Identification of friction points where customers frequently need to rephrase
   - Detection of common "dead ends" or circular conversations
   - Comparison of optimal vs. actual conversation paths

2. **Time-Based Metrics**
   - **Response Time**: Average time to generate agent responses (target: <3 seconds)
   - **Time to Resolution**: Average time from conversation start to successful task completion
   - **Peak-Time Performance**: Metrics segmented by time of day to identify performance variations
   - **Seasonal Trends**: Tracking performance changes during high-volume periods

3. **Business Impact Metrics**
   - **Cost Per Conversation**: Total operating cost divided by number of conversations
   - **Cost Savings**: Comparison with traditional customer service channels
   - **Revenue Influence**: Conversion rate when agent recommends products
   - **Customer Retention Impact**: Correlation between agent usage and repeat purchases

## Customer Prioritization

Please prioritize the remaining customer feature requests, share how you choose to prioritize them, and what additional information you would seek before implementation.

Assuming the required feature (Order Status) and two optional features have been implemented, here's how I'd prioritize the remaining features:

1. **Product Recommendations**: Highest priority as it directly impacts sales and customer satisfaction. It leverages existing product catalog data and enhances the shopping experience.

2. **Hiking Recommendations**: Aligns perfectly with Sierra's brand identity and could drive engagement, though it's more complex to implement effectively.

3. **Multilingual Support**: While valuable for accessibility, I'd prioritize this last as it requires significant testing and may have more limited impact depending on customer demographics.

Before implementation, I would seek:
- Usage analytics showing the frequency of requests related to each feature
- Customer demographic data to understand the potential impact of multilingual support
- Current conversion rates from product inquiries to sales to better quantify the value of product recommendations
- Feedback from customer service team on what questions they most frequently handle