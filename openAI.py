
import openai
import os
import json

# Set API key
openai.organization = "org-9DDsktpOgd7k6423x7ZIYwoI"
openai.api_key = os.environ["OPENAI_API_KEY"]

def create_product(title, price, category):
    print('Invoke create_product function...')
    return json.dumps(
        {
            "title": title,
            "price": price,
            "category": category,
        }
    )

# dummy function for testing only
def update_product(title, price, category):
    print('Invoke update_product function...')
    return json.dumps(
        {
            "title": title,
            "price": price,
            "category": category,
            "product_id": 123
        }
    )

def sendMsgToChatGPT(messages):
    print('sendMsgToChatGPT(messages) ', messages)
    
    kwargs = {
        "model": "gpt-3.5-turbo-0613", 
        "messages": messages,
        "temperature": 1,
         "functions": [{
                "name": "create_product",
                "description": "The `create_product` function enables users to add a new product to the database. This function takes three required parameters and few optional parameters. the required parameters are `name`, `price`, `category`. The optional parameters are `variants`, `sale price`. ",
                #The function validates the input parameters before creating a product. If any of the parameters is not provided, an error message will be returned indicating the missing parameters. If all parameters are valid, it constructs a product object and adds it to the product database. The function then returns a success message along with the newly created product's details.
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string", 
                            "description": "Specifies the name of the product. It should be unique to distinguish the product from others."
                        },
                        "categories": {
                            "type": "string",
                            "description": "Represents the category to which the product belongs. This helps in grouping similar products for easier navigation and management.",
                            "items": {
                                "type": "string"
                            },
                        },
                        "price": {
                            "type": "number",
                            "description": "Indicates the selling price of the product. It must be a non-negative number, representing the cost in dollars.",
                        },
                        "sale_price": {
                            "type": "number",
                            "description": "Sale price for given product, it's optional, but must be lower than price, default is 0 is not specified",
                        },
                        "description": {
                            "type": "string",
                            "description": "Product description (optional), default should be empty string if not specified",
                        },
                        "stock_quantity": {
                            "type": "number",
                            "description": "Must be an integer and greater or equal to 0 (optional), default should be null, unless specified explicitly",
                        },
                        "weight": {
                            "type": "number",
                            "description": "Product weight in grams (optional), default should be null, unless specified explicitly",
                        },
                        "per_item_type": {
                            "type": "string",
                            "enum": ["piece", "kg", "gm", "set", "dozen"],
                            "description": "Product unit, default should piece if not specified",
                        },
                        "per_item_quantity": {
                            "type": "number",
                            "description": "Product unit quantity, default is 1 if not specified, must be greater or equal to 1",
                        },
                        "variants": {
                            "type": "array",
                            "description": "Product variants, maximum can have 3 different variant types, must be unique (optional)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "variant_type": {
                                        "type": "string",
                                        "description": "Variant type",
                                    },
                                    "options": {
                                        "type": "array",
                                        "description": "Variant options, must have at least one option, can have maximum of 10 options, must be unique, cannot repeat",
                                        "items": {
                                            "type": "string",
                                            "description": "Variant option",
                                        },
                                    },
                                },
                            },
                        }, # variants
                    },
                },
                "required": ["title", "categories", "price"],
                }],
        
            
            # "function_call": "none"
    }
    # Generate model response
    response = openai.ChatCompletion.create(**kwargs)
    
    print("=========== response: ", response)
    # Extract the model's message from the response
    model_message = response["choices"][0]["message"]
    print("=========== model_message: ", model_message)
    if model_message.get("function_call"):
        print("======== function_call here: ")
         # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "create_product": create_product,
            "update_product": update_product,
        }  # only one function in this example, but you can have multiple
        function_name = model_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(model_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            title=function_args.get("title"),
            price=function_args.get("price"),
            category=function_args.get("category"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(model_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        messages.append(
            {
                "role": "system",
                "content": "compose product link using id returned from function, in format ```shopboxo.io/product/<id>```, then return this URL in the response",
            }
        ) 
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response

        print("=========== second_response: ", second_response)
        return second_response
    
    # Print the model's message
    print(">> AI: ", model_message.content)
    return model_message
    
    


