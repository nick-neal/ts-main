class Config(object):
    DEBUG = False
    TESTING = False

class DevConfig(Config):
    DEBUG = True
    ENV = 'development'

class TestConfig(Config):
    TESTING = True
    ENV = 'test'

class ProdConfig(Config):
    ENV = 'production'
