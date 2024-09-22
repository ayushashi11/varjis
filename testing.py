import dotenv, os
from typing import Optional, Union
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
dotenv.load_dotenv()

from typing_extensions import Annotated, TypedDict


class add(TypedDict):
    """Add two integers."""

    # Annotations must have the type and can optionally include a default value and description (in that order).
    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


class multiply(BaseModel):
    """Multiply two integers."""

    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


tools = [add, multiply]

llm = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.environ["TOGETHER_API_KEY"],
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

query = "What is 3 * 12?"

print(llm_with_tools.invoke(query).tool_calls)
