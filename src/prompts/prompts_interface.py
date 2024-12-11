from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
from .base_config import BasePromptConfig

class PromptsInterface(ABC):
    def __init__(self, config: BasePromptConfig = None):
        self._config = config if config is not None else BasePromptConfig.get_instance()
    
    @property
    def reward(self) -> str:
        """
        Get the reward for the models, this a a prompt tecnique to reward the model for the correct behavior
        """
        return self._config.reward
    
    @property
    def security_instructions(self) -> str:
        """
        Get the security instructions for the models, this is a set of rules and limitations to the model behavior
        """
        return self._config.security_instructions
    
    @property
    def output_language(self) -> str:
        """
        Get the default language for the models, this is the language that the models will use to respond. Unless another language is specified.
        """
        return self._config.output_language

    @abstractmethod
    def get_prompt(self) -> PromptTemplate:
        """
        Get the prompt for the agent, this is the prompt that the agent will use to respond.
        """
        pass


