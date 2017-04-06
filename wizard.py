import os
import sys
import fnmatch
import xml.etree.ElementTree as ET
from descriptors import *
from xml_templates import *
import logger

core_project_map = {}


# checks whether the input str matches with pattern
def match_string_with_pattern(str, pattern):
    return fnmatch.fnmatch(str, pattern)


# returns a list of files in root that match the given pattern
def find_files_with_pattern(root, pattern, matched_files,
                            lookup_recursively=True):
    for entry in os.scandir(root):
        if entry.is_dir() and lookup_recursively:
            find_files_with_pattern(entry.path, pattern, matched_files)
        elif match_string_with_pattern(entry.name, pattern):
            matched_files.append(entry)


def get_nuget_cache_path(solution_dir):
    nuget_config_files = []
    find_files_with_pattern(solution_dir, "NuGet.config", nuget_config_files)

    if len(nuget_config_files) == 0:
        return solution_dir + "\\packages\\"
    elif len(nuget_config_files) == 1:
        nuget_config_file = nuget_config_files[0]
        tree = ET.parse(nuget_config_file.path)
        root = tree.getroot()
        for config_section in root.findall("config"):
            for config_record in config_section.findall("add"):
                if config_record.attrib["key"] == "repositoryPath":
                    return config_record.attrib["value"]

    # TODO Handle the case when there are multiple NuGet.configs in
    # a single solution hierarchy.


# gets the assembly descriptor project file
def get_assembly_descriptor(project_file):
    tree = ET.parse(project_file.path)
    root = tree.getroot()
    for property_group_element in root.findall(property_group_tag):
        if len(property_group_element.findall(assembly_name_tag)) > 0:
            name = property_group_element.find(assembly_name_tag).text
            output_type = property_group_element.find(output_type_tag).text
            guid = property_group_element.find(project_guid_tag).text
            project_file_name = os.path.splitext(project_file.name)[0]
            assembly = Assembly(name, guid, output_type,
                                project_file, project_file_name)
            return assembly
    return None


def add_project_to_sln(solution_file_name, assembly):
    sln_file = open(solution_file_name, "a")
    sln_file.write(
        get_sln_project_reference_text(
            lib_project_type_guid, assembly.name,
            assembly.project_file.path, assembly.guid))
    sln_file.close()


# replaces core nuget dll references with project references
def replace_core_references(project_file):
    ET.register_namespace('', csproj_xml_namespace)
    tree = ET.parse(project_file.path)
    root = tree.getroot()
    item_groups = root.findall(item_group_tag)
    project_reference_item_groups = [group for group in item_groups if
                                     len(group.findall(project_ref_tag)) > 0]
    lib_reference_item_groups = [group for group in item_groups
                                 if len(group.findall(reference_tag)) > 0]

    removed_libs = set()
    # finding and removing lib references
    for lib_reference_item_group in lib_reference_item_groups:
        for reference in lib_reference_item_group.findall(reference_tag):
            lib_name = reference.attrib["Include"].split(",")[0]
            if lib_name in core_project_map:
                lib_reference_item_group.remove(reference)
                removed_libs = removed_libs.union([lib_name])
                logger.log_info("Removed reference to {} from {}".format(
                    lib_name, project_file.name))

    # adding project references for removed libs
    if len(project_reference_item_groups) > 0:
        project_reference_item_group = project_reference_item_groups[0]
        for lib in removed_libs:
            assembly = core_project_map[lib]
            element = get_project_reference_element(assembly.project_file.path,
                                                    assembly.guid,
                                                    assembly.project_file_name)
            project_reference_item_group.append(element)
            logger.log_info("Added project reference for {} in {}".format(
                lib, project_file.name))

    # TODO Handle the case when there's no item group with project refs
    logger.log_info("Saving changes to {}".format(project_file.path))
    tree.write(project_file.path)


# entry point for the program
def main(core_directory, solution_path):
    solution_directory = os.path.dirname(solution_path)
    logger.log_info("Starting the wizardry...")

    logger.log_info("Looking for project files in library solution.")
    core_project_files = []
    find_files_with_pattern(core_directory, "*.csproj", core_project_files)
    logger.log_info("Found {} project files".format(len(core_project_files)))
    logger.log_list([m.name for m in core_project_files])

    logger.log_info("Inspecting assemblies for library projects.")
    for project_file in core_project_files:
        assembly = get_assembly_descriptor(project_file)
        core_project_map[assembly.name] = assembly

    referenced_libs = []
    logger.log_info("Searching for NuGet package cache.")
    package_cache_path = get_nuget_cache_path(solution_directory)
    logger.log_info("NuGet package cache found in {}.".format(
        package_cache_path))
    logger.log_info("Compiling a list of assemblies in package cache.")
    find_files_with_pattern(package_cache_path, "*.dll", referenced_libs)

    added_libs = []
    logger.log_info("Adding project references to solution file:")
    for lib in referenced_libs:
        lib_file_name = os.path.splitext(lib.name)[0]
        if (lib_file_name in core_project_map and
                lib_file_name not in added_libs):
            add_project_to_sln(solution_path, core_project_map[lib_file_name])
            added_libs.append(lib_file_name)
    logger.log_list(["{} - OK".format(m) for m in added_libs])

    logger.log_info("Looking up projects that refer to NuGet " +
                    "packages in solution directory.")
    package_files = []
    find_files_with_pattern(solution_directory,
                            "packages.config", package_files)
    project_files = []
    project_dirs = [os.path.dirname(entry.path) for entry in package_files]

    for project_dir in project_dirs:
        csproj_files = []
        find_files_with_pattern(project_dir, "*.csproj", csproj_files, False)
        project_files.extend(csproj_files)

    logger.log_info("Found {} projects that refer to NuGet packages".format(
        len(project_files)))
    logger.log_list([m.path for m in project_files])

    logger.log_info("Replacing NuGet lib references with " +
                    "project references in affected project files.")
    for project_file in project_files:
        replace_core_references(project_file)

    logger.log_info("Task completed successfuly! " +
                    "No unicorns harmed in the process.")


core_dir = sys.argv[1]
solution_path = sys.argv[2]
main(core_dir, solution_path)
