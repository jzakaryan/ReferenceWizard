from collections import namedtuple

Assembly = namedtuple(
    typename="Assembly",
    field_names="name guid output_type project_file project_file_name")

Package = namedtuple(
    typename="Package",
    field_names="name version")
