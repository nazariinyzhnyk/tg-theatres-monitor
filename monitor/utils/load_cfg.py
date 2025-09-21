from pathlib import Path

import yaml


def load_yaml_config(conf_file_path: Path | None = None) -> dict:
    """
    Load configuration from a YAML file.
    Parameters
    ----------
    conf_file_path: Path | None
        Path to the configuration file. If None, defaults to 'theatres_cfg.yaml' in
        the current directory.

    Returns
    -------
    dict
        Parsed configuration dictionary.
    """

    if conf_file_path is None:
        conf_file_path = Path(__file__).parent.parent / "theatres_cfg.yaml"  # type: ignore

    if not conf_file_path.exists():  # type: ignore
        raise FileNotFoundError(f"Config file not found within path: {conf_file_path}")

    with open(conf_file_path, "r") as conf_file_path:  # type: ignore
        cfg = yaml.safe_load(conf_file_path)  # type: ignore

    return cfg
