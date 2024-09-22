from pydantic_core import from_json
from pydantic import BaseModel, Field, Json

class Output(BaseModel):
    is_only_tool: bool = Field(default=False, description="Whether this output is only a tool call")
    message: str = Field(default="", description="The message to be displayed and spoken")
    images: list[str] = Field(default_factory=lambda:[], description="The images(urls) to be displayed")
    tool_name: str = Field(default="", description="The name of the tool to be called")
    parameters: dict = Field(default_factory=lambda: {}, description="The parameters to be passed to the tool")

def parse(text: str) -> tuple[Output, bool]:
    partial = False
    try:
        js = from_json(text)
    except ValueError:
        partial = True
        js = from_json(text+'"', allow_partial=True)
    return Output.model_validate(js), partial

if __name__ == "__main__":
    print(parse('{"message": "hello", "parameters": {"keywords": "hello", "max_results'))
    print(Output.model_json_schema())