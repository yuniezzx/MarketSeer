import yaml

def load_config(config_path="config/settings.yaml") -> dict:
    """
    加载 YAML 配置文件，返回字典
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config