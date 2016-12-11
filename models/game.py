class GameConfig(object):
    def __init__(self, name, description, author, version, robot_model, robot_system, game_requirements, lego_construction):
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.robot_model = robot_model
        self.robot_system = robot_system
        self.game_requirements = game_requirements
        self.lego_construction = lego_construction


class GameRelese(GameConfig):
    def __init__(self, name, description, author, version, robot_model, robot_system, game_requirements, lego_construction):

        super(GameRelese,self).__init__(name, description, author, version, robot_model, robot_system, game_requirements, lego_construction)