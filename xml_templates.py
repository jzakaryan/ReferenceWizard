import xml.etree.ElementTree as ET

csproj_xml_namespace = "http://schemas.microsoft.com/developer/msbuild/2003"

property_group_tag = "{{{}}}PropertyGroup".format(csproj_xml_namespace)
assembly_name_tag = "{{{}}}AssemblyName".format(csproj_xml_namespace)
output_type_tag = "{{{}}}OutputType".format(csproj_xml_namespace)
project_guid_tag = "{{{}}}ProjectGuid".format(csproj_xml_namespace)
item_group_tag = "{{{}}}ItemGroup".format(csproj_xml_namespace)
project_ref_tag = "{{{}}}ProjectReference".format(csproj_xml_namespace)
reference_tag = "{{{}}}Reference".format(csproj_xml_namespace)

lib_project_type_guid = "FAE04EC0-301F-11D3-BF4B-00C04F79EFBC"

# csproj templates
project_reference_tag_template = "<ProjectReference Include=\"{}\">\n\t\t" \
    "<Project>{}</Project>\n\t\t<Name>{}</Name>\n</ProjectReference>\n"


def get_project_reference_element(csproj_path, project_guid, csproj_name):
    element_str = project_reference_tag_template.format(
        csproj_path, project_guid, csproj_name)
    return ET.fromstring(element_str)


# sln templates
sln_project_ref_template = "Project(\"{{{}}}\") = \"{}\"," \
    " \"{}\", \"{}\"\nEndProject\n"


def get_sln_project_reference_text(project_type_guid,
                                   project_name,
                                   project_file_name,
                                   project_guid):
    return sln_project_ref_template.format(
        project_type_guid, project_name, project_file_name, project_guid)
