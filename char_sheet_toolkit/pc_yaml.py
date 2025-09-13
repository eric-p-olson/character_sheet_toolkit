import yaml


def write_pc_yaml(yaml_output_file, pc_data):
    with open(yaml_output_file, "w") as yaml_output_file:
        yaml.dump(dict(pc_data), yaml_output_file, default_flow_style=False)


def read_pc_yaml(yaml_input_file, pc_data):
    pc_data.clear()
    with open(yaml_input_file, "r") as yaml_input_file:
        pc_data.update(yaml.safe_load(yaml_input_file))
