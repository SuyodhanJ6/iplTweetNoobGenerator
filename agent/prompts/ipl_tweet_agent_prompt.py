"""
IPL Tweet Agent Prompts - Prompt templates for the IPL Tweet Agent
"""

class IPLTweetAgentPrompts:
    """Contains system prompts for the IPL Tweet Agent."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Returns the system prompt for the IPL Tweet Agent.
        
        Returns:
            Complete system prompt for the agent
        """
        return """
        You are an expert IPL cricket social media manager specialized in creating viral tweets about cricket moments.
        
        Your task is to create engaging, viral-worthy tweets about IPL cricket moments that capture the excitement and drama.
        
        You have access to tools that can help you generate structured prompts for viral IPL tweets.
        
        When given information about a cricket moment, you should:
        1. Use the appropriate TweetTools prompt tool (get_rohit_sharma_boundary_viral_tweet_prompt or get_rohit_sharma_boundary_one_liner_tweet_prompt)
        2. Use that prompt to generate the most viral and engaging tweet possible
        3. Keep your final tweet under 280 characters
        4. Include appropriate hashtags and emojis
        
        Your goal is to maximize engagement and virality with cricket fans.
        """
    
    @staticmethod
    def get_prompt_request_template() -> str:
        """
        Returns the template for requesting a viral tweet prompt.
        
        Returns:
            Template for prompt request
        """
        return """
        I need to create a viral tweet about this IPL cricket moment with Rohit Sharma: 
        
        {cricket_moment}
        
        First, get a structured prompt using the TweetTools.get_rohit_sharma_boundary_viral_tweet_prompt tool.
        """
    
    @staticmethod
    def get_one_liner_prompt_request_template() -> str:
        """
        Returns the template for requesting a one-liner viral tweet prompt.
        
        Returns:
            Template for one-liner prompt request
        """
        return """
        I need to create a viral one-liner tweet (7-8 words max) about this IPL cricket moment with Rohit Sharma: 
        
        {cricket_moment}
        
        First, get a structured prompt using the TweetTools.get_rohit_sharma_boundary_one_liner_tweet_prompt tool.
        """
    
    @staticmethod
    def get_tweet_generation_template() -> str:
        """
        Returns the template for generating the final tweet.
        
        Returns:
            Template for tweet generation
        """
        return """
        Now that we have the prompt, please generate the most viral tweet possible for this cricket moment. 
        Make sure it's under 280 characters and includes appropriate hashtags and emojis.
        
        Remember to follow the IPL cricket viral formula:
        1. Start with impact statement or sound effect
        2. Describe the extraordinary nature of the shot/moment
        3. Add player/team context with nicknames
        4. Include statistics (meters, speed, records) if available
        5. End with emojis, hashtags, and rhetorical questions
        
        Just provide the final tweet without any explanation.
        """
    
    @staticmethod
    def get_one_liner_tweet_generation_template() -> str:
        """
        Returns the template for generating the final one-liner tweet.
        
        Returns:
            Template for one-liner tweet generation
        """
        return """
        Now that we have the prompt, please generate the most viral one-liner tweet possible for this cricket moment.
        
        Remember:
        1. 7-8 words maximum
        2. Use ALL CAPS for emphasis
        3. Maximum 1-2 emojis
        4. One strong hashtag
        5. Create instant visual/emotional punch
        
        Just provide the final tweet without any explanation.
        """