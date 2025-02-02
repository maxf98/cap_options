

class EnvironmentAgent:
    """
    responsible for aiding in environment setup
    like the actor, should get better and better at setting the environment to a specific configuration
    tailored to the creator - it learns a specific language, i.e. a mapping from NL to env-config 
    (through API + retrieval - including past configs)
    """