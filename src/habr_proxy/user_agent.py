

class BaseUserAgentProvider:

    def get_user_agent(self):
        raise NotImplementedError()


class DefaultUserAgentProvider:

    def get_user_agent(self):
        return 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'


def get_default_user_agent_provider():
    return DefaultUserAgentProvider()
