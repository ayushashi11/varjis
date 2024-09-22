#Tool metadat fpr the llm
mathTool = {
    "name": "math",
    "description": "give the system mathematical operations"
    " to evaluate based on what the user is asking. The user"
    " may explicitly state the formula by prepending an = sign"
    " to the input or may ask a generic question such as"
    " converting centimeters to feets and inches. The tool may"
    " pass multiple formulas as well. The formulas should be in"
    " a pythonic syntax(assume `from math import *` and"
    " `from sympy import *` are already imported). Example:"
    " if the user asks you to convert 189cm to feets and inches,"
    " the formulas would be"
    "{\"feet\": \"floor(189/30.48)\", \"inches\": \"189/2.54-12*floor(189/30.48)\"}"
    " and the units would be"
    "{\"feet\": \"feet\", \"inches\": \"inches\"}"
    " as seen above when multiple related units are given that"
    " frequently occur together like feets and inches or"
    " centimeters and meters, the system should break"
    " the answer into larger and smaller parts. Like"
    " 184cm should be converted to 1m 84cm or 6feet 0.4inches",
    "parameters": {
        "type": "object",
        "properties": {
            "formulas": {
                "type": "object",
                "description": "The formulas to evaluate",
            },
            "units": {
                "type": "object",
                "description": "The units in which the answers are",
            },
        },
        "required": ["formulas", "units"],
    }
}

commandTool = {
    "name": "command",
    "description": "give the linux commands to run based off"
    " user input. The user may directly ask the system to run"
    " a command by prepending tthe input with r: or may ask"
    " a question that requires a command to be run(like for"
    " example, update the system packages)",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "list[str]",
                "description": "The command to run, arguments separated in a list form so it can be passed to subprocess.Popen",
            },
            "sudo_flag": {
                "type": "boolean",
                "description": "Whether to run the command with sudo",
            },
            "stdin": {
                "type": "string",
                "description": "The input to be given to the command(optional)",
            }
        },
        "required": ["command", "sudo_flag"],
    }
}

wikipediaTool = {
    "name": "wikipedia",
    "description": "give the system a topic to search on"
    " wikipedia and return the summary of the topic"
    " and some images related to the topic."
    " Use [^ line1:column1 - line2:column2 ^] after a"
    " line in the summary to map that part of the summary"
    " to the original wikipedia article, from where the line"
    " was extracted. The user may also ask for the"
    " wikipedia article to be summarized in a specific"
    " language",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic to search on wikipedia",
            },
        },
        "required": ["topic"],
    }
}

newsTool = {
    "name": "news",
    "description": "Give the system keywords to search news on duckduckgo"
    " Dont forget to mention the source of the article"
    " using the markdown link syntax like [source](url)",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "The keywords to search news on duckduckgo",
            },
            "max_results": {
                "type": "int",
                "description": "The maximum number of results to return",
            }
        },
        "required": ["keywords"],
    }
}

searchTool = {
    "name": "search",
    "description": "Give the system keywords to search on duckduckgo",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "The keywords to search on duckduckgo",
            },
            "max_results": {
                "type": "int",
                "description": "The maximum number of results to return",
            }
        },
        "required": ["keywords"],
    }
}

editApplicationSettingsTool = {
    "name": "editApplicationSettings",
    "description": "Edit the application/user/bot settings or knowledge"
    " the settings is a key value json storage",
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The key to edit",
            },
            "value": {
                "type": "string|list|object",
                "description": "The value to set",
            }
        },
        "required": ["key", "value"],
    }
}

removeApplicationSettingsTool = {
    "name": "removeApplicationSettings",
    "description": "Remove the application/user/bot settings or knowledge"
    " the settings is a key value json storage",
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The key to remove",
            },
        },
        "required": ["key"],
    }
}
