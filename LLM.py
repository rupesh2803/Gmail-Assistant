from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document

def load_result(original_body):
    prompt_template = """
    ### Email Content:
    Body:
    {body}

    ### Guidelines for the Response:
    1. Address the sender politely using "Hi [Sender's Name]," or "Hello," if the name isn't available.
    2. Provide a clear and concise answer to the question in the email.
    3. If the email has multiple questions, address them one by one in the same response.
    4. If the email contains a general request for information, provide a brief but informative reply.
    5. Sign off with "Best regards," followed by a generic name like "Your Chatbot :)" unless instructed otherwise.

    ### Your Response:
    [Generate the response here based on the email content above]
    """
    
    model = ChatOllama(model="llama3.2:latest", temperature=0.3)
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["body"])

    llm_chain = LLMChain(llm=model, prompt=prompt)

    response = llm_chain.invoke({"body": original_body})
    
    return (response['text'])

