import math
import re
import os

import semantic_version
from yaml import dump

from werckercli.client import Client
from werckercli.cli import get_term, puts
from werckercli.config import DEFAULT_WERCKER_YML
from werckercli.decorators import yaml_required


class TransportError(Exception):
    pass


def validate_box_name(name, validate_web=False, version=0):

    unversioned_pattern = "^[a-zA-Z0-9]+/[A-z0-9][A-z0-9-.]+[A-z0-9]$"

    match = re.match(unversioned_pattern, name)

    if validate_web is False:
        return match is not None
    else:
        if match:
            c = Client()
            response, result = c.get_box(name, version)

            if response == 404:
                return False
            else:
                if result:
                    return True
                else:
                    raise TransportError("Unexpected response from server")
        else:
            return False


def search_services(name):

    client = Client()

    term = get_term()

    response, results = client.get_boxes()

    if results and len(results):
        services = filter(
            lambda box: box.get("latestType", "") == "service",
            results
        )
        services = sorted(
            services,
            key=lambda service: service.get("fullname")
        )

        if name:
            services = filter(
                lambda box: (
                    box.get("fullname", "").find(name) != -1 or
                    box.get("latestDescription").find(name) != -1
                ),
                services
            )

        if len(services) is not 0:
            if term.width:
                pad_length = term.width * 0.2
                pad_length = int(math.floor(pad_length))
                pad_length = max(pad_length, 30)
                pad_length = min(pad_length, 50)
            else:
                pad_length = 0

            for service in services:
                # versions = service.get("versionNumbers")
                versions = get_sorted_versions(service)

                if len(versions):
                    detailName = service["fullname"]
                    paddedName = detailName.ljust(pad_length)

                    if name:
                        paddedName = paddedName.replace(
                            name,
                            term.bold_white + name + term.normal
                        )

                    description = service["latestDescription"]
                    if description is None:
                        description = ""

                    version = versions[len(versions)-1]
                    version = str(version)
                    version = version.rjust(8)
                    if name:
                        description = description.replace(
                            name,
                            term.bold_white + name + term.normal
                        )

                    puts(
                        paddedName + " - " + version + " - " +
                        description
                    )

        else:
            if name:
                puts(
                    "No services found with: {t.bold_white}{0}{t.normal}".
                    format(
                        name,
                        t=term
                    )
                )
            else:
                puts("No services found.")


def putInfo(label, data, multiple_lines=False):
    term = get_term()

    paddedLabel = str(label) + ":"
    paddedLabel = paddedLabel.ljust(20)

    if multiple_lines is True:
        seperator = "\n"
    else:
        seperator = ""

    puts("{t.bold}{t.white}{label}{t.normal}{seperator}{data}".format(
        label=paddedLabel,
        seperator=seperator,
        data=data,
        t=term)
    )


def info_service(name, version=0):

    term = get_term()
    valid = False

    valid = validate_box_name(name)

    if valid is False:
        puts(
            "{t.red}Error: {t.normal} {name} is not a valid service name"
            .format(
                t=term,
                name=name
            )
        )
        return

    client = Client()

    puts("Retrieving service: {t.bold_white}{name}\n".format(
        # owner=owner,
        name=name,
        t=term)
    )
    response, results = client.get_box(name, version=version)

    if response == 404:
        puts(term.yellow("Warning: ") + "service not found.")
    elif results.get("type") != "service":
        puts(term.yellow("Warning: ") + "found box was not a service.")
    elif results:
        response, release_info = client.get_box_releases(name)
        if results:
            putInfo("Fullname", results.get("fullname"))
            putInfo("Owner", results.get("owner"))
            putInfo("Name", results.get("name"))
            puts("")
            putInfo(
                "All versions",
                '\n'.join(release_info.get("versionNumbers")),
                multiple_lines=True
            )
            putInfo("showing version", results.get("version"))
            puts("")

            license = results.get("license")
            if license is None:
                license = "none specified"
            putInfo("License", license)

            keywords = ", ".join(results.get("keywords"))
            if keywords is None:
                keywords = ""

            putInfo("Keywords", keywords)
            putInfo(
                "\nDescription",
                results.get("description"),
                multiple_lines=True
            )

            packages = ""

            for package in results.get("packages"):
                if len(packages):
                    packages += ", "

                packages += "{name}: {version}".format(
                    name=package.get("name"), version=package.get("version")
                )
            else:
                packages = "None specified"

            putInfo("\nPackages", packages, multiple_lines=True)
            putInfo("\nRead me", results.get("readMe"), multiple_lines=True)
    else:
        puts("{t.red}Error: {t.normal}An error occurred while retrieving \
service information")


def get_sorted_versions(box):
    versions = box.get("versionNumbers", [])

    sem_versions = []
    rejected = []
    for version in versions:
        try:
            sem_version = semantic_version.Version.coerce(version)
            sem_versions.append(sem_version)
        except ValueError:
            rejected.append(version)

    sem_versions = sorted(
        sem_versions,
        # key=lambda version: semantic_version.Version.coerce(version)
    )

    if len(rejected):
        puts(
            "{t.yellow}Warning: {t.normal}Unable to parse version values \
{versions} for {fullname}"
            .format(
                t=get_term(),
                versions=', '.join(rejected),
                fullname=box.get('fullname', '')
            )
        )

    return sem_versions


def check_service(service, result=None):
    term = get_term()

    if not result:
        c = Client()
        _response, result = c.get_boxes()

    unversioned_pattern = "(?P<owner>.*)/(?P<name>.*)"
    versioned_pattern = "(?P<owner>.*)/(?P<name>.*)@(?P<version>.*)"

    results = re.search(versioned_pattern, service)

    if not results:
        results = re.search(unversioned_pattern, service)

    info_dict = results.groupdict()

    if not result:
        puts("""{t.red}Error:{t.normal}""".format(t=term))
    else:
        fullname = "{owner}/{name}".format(
            owner=info_dict.get("owner"),
            name=info_dict.get("name")
        )

        boxes = filter(
            lambda box: box.get("fullname") == fullname,
            result
        )

        if len(boxes) == 0:
            puts("""{t.yellow}Warning:{t.normal} Service \
{fullname} not found.""".format(
                t=term)
            )

        else:
            box = boxes[0]

            versions = get_sorted_versions(box)
            latest_version = False
            specified_version = info_dict.get("version", None)

            if not specified_version:
                version_found = len(versions) > 0
                # latest_version = versions[len(versions)-1]
                requested_version = versions[len(versions)-1]
            else:

                version_found = False
                try:
                    requested_version = semantic_version.Version.coerce(
                        specified_version,
                    )
                except ValueError:
                    requested_version = None

                if requested_version:
                    spec = semantic_version.Spec(
                        '==' + str(specified_version)
                    )
                else:
                    try:
                        spec = semantic_version.Spec(
                            str(specified_version)
                        )
                    except ValueError:
                        puts(
                            """{t.red}Error: {t.normal}Invalid version \
specification detected: {version}.
Expected a SemVer version or specification (i.e. 0.1.2 or >0.1.1)
For more information on SemVer see: http://semver.org/"""
                            .format(
                                t=term,
                                version=requested_version
                            )
                        )
                        return

                # print locals()
                requested_version = spec.select(versions)

                if requested_version:
                    version_found = True

                    newer_spec = semantic_version.Spec(
                        ">" + str(requested_version)
                    )
                    latest_version = newer_spec.select(versions)

                    if not latest_version:
                        latest_version = False
                else:
                    version_found = False

            if version_found is False:
                info = "{t.red}not found{t.normal}".format(
                    t=term
                )
            elif latest_version is not False:
                info = "{t.yellow}upgrade to {sem_ver}{t.normal}".\
                    format(
                        t=term,
                        sem_ver=latest_version
                    )
            else:
                info = "{t.green}latest{t.normal}".format(t=term)
            puts(
                "{fullname} - {version} ({info}) - {description}".
                format(
                    fullname=fullname,
                    info=info,
                    version=requested_version,
                    description=box.get("latestDescription")
                )
            )


@yaml_required
def list_services(path=".", yaml_data=None, str_data=None):
    # pass

    term = get_term()

    if str_data is None:
        return

    if yaml_data is None:
        return

    services = yaml_data.get("services")

    if not services:
        puts(
            "{t.yellow}Warning:{t.normal} No services specified in the \
{yaml}".
            format(
                yaml=DEFAULT_WERCKER_YML,
                t=term
            )
        )
    else:
        if type(services) is str:
            services = [services]

        puts("Services currently in use:\n")
        check_services(services)


def update_yaml(path, str_data, yaml_data, new_services):
    lines = str_data.splitlines()

    filtered_lines = []
    blocking = False

    for line in lines:
        if re.match('^services[ ,\t]?:[ ,\t]?', line):
            blocking = True
        elif re.match('^[A-Za-z][A-Za-z0-9]', line):
            blocking = False
        if blocking is False:
            filtered_lines.append(line)

    if new_services is None or len(new_services) == 0:
        lines = filtered_lines
    else:
        services = {"services": new_services}
        services = dump(
            services,
            default_flow_style=False,
            explicit_start=False
        )
        services = re.sub(r'\n$', '', services)

        lines = []
        for line in filtered_lines:

            if re.match('^box[ ,\t]?:[ ,\t]?', line):
                line += "\n" + services

            lines.append(line)

    out = '\n'.join(lines)

    fh = open(os.path.join(path, DEFAULT_WERCKER_YML), 'w')
    fh.write(out)
    fh.close()


@yaml_required
def add_service(
    name, version=0, path=".", str_data=None, yaml_data=None
):
    if str_data is None:
        return

    if yaml_data is None:
        return

    term = get_term()
    valid = False

    try:
        valid = validate_box_name(name, version=version, validate_web=True)
    except TransportError:
        puts(
            "{t.red}Error: {t.normal} An error occured while communicating \
with the server".format(t=term)
        )
        return

    if valid is False:
        if version != 0:
            puts(
                """{t.red}Error: {t.normal} service {service} matching \
{version} not found.
Service not added"""
                .format(
                    t=term,
                    service=name,
                    version=str(version)
                )
            )
        else:
            puts(
                """{t.red}Error: {t.normal} service {service} not found.
Service not added"""
                .format(
                    t=term,
                    service=name,
                    version=str(version)
                )
            )

        return
    current_service = yaml_data.get("services")

    specific_service = "{name}".format(
        name=name
    )

    updated = False

    if(version != 0):
        specific_service += "@" + version

    specific_regex = "^{name}(@)?".format(name=name)

    if current_service:

        if type(current_service) is str:
            if re.match(specific_regex, current_service):
                updated = True
                new_services = specific_service
            else:
                new_services = [specific_service, current_service]
        else:
            new_services = []
            for service in current_service:
                if re.match(specific_regex, service):
                    updated = True
                    new_services.append(specific_service)
                else:
                    new_services.append(service)

            if updated is not True:
                new_services.append(specific_service)
    else:
        new_services = specific_service

    update_yaml(path, str_data, yaml_data, new_services)

    if updated:
        puts(
            """{t.green}Succes:{t.normal} Service {service} {t.bold_white}\
updated{t.normal} in {file}"""
            .format(
                t=term,
                file=DEFAULT_WERCKER_YML,
                service=specific_service,
            )
        )

    else:
        puts(
            """{t.green}Succes:{t.normal} Service {service} added to {file}"""
            .format(
                t=term,
                file=DEFAULT_WERCKER_YML,
                service=specific_service,
            )
        )


@yaml_required
def remove_service(
    name, path=".", str_data=None, yaml_data=None
):
    if str_data is None:
        return

    if yaml_data is None:
        return

    term = get_term()
    current_service = yaml_data.get("services")

    if current_service:

        specific_service = "{name}".format(
            name=name
        )

        service_regex = "^({service})(@)?".format(
            service=specific_service
        )

        found = False
        new_services = current_service
        if type(current_service) is str:
            if re.match(service_regex, current_service):
                found = True
                new_services = None
        else:
            new_services = []
            for service in current_service:
                if re.match(service_regex, service):
                    found = True
                else:
                    new_services.append(service)
        if found:
            update_yaml(path, str_data, yaml_data, new_services)
            puts(
                "{t.green}Succes:{t.normal} Service {service} removed."
                .format(
                    service=specific_service,
                    t=term,
                )
            )
        else:
            puts(
                "{t.yellow}Warning: {t.normal}service {service} is not found".
                format(
                    service=specific_service,
                    t=term
                )
            )


def check_services(services):

    term = get_term()
    c = Client()

    response, result = c.get_boxes()

    for service in services:

        if len(service.splitlines()) > 1:
            puts("""{t.yellow}Warning:{t.normal} Incorrect service \
specification detected.
Reason: A new line detected in declaration:
{service}""".format(t=term, service=service))

        else:
            check_service(service, result)
        # if
    if services is None or len(services) == 0:
        puts(
            """{t.yellow}Warning:{t.normal} No services specified in {file}"""
            .format(
                t=term,
                file=DEFAULT_WERCKER_YML
            )
        )
