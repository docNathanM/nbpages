import os
import datetime
import shutil
import configparser

index_md_tpl = """
[//]: # (DO NOT EDIT. index.md is generated by nbpages. Make changes to templates/index.md.tpl.)
# {{ page_title }}

{% for line in readme_toc -%}
{{ line }}
{% endfor %}

"""

notebook_header_tpl = """
*This notebook contains material from [{{ page_title }}]({{ page_url }});
content is available [on Github]({{ github_url }}).*

"""

nbpages_tpl = """
<!-- jinja2 template extends `full` to include cell tags in the html rendering of notebooks -->
{% extends 'full.tpl'%}
{% block any_cell %}
{% if cell['metadata'].get('tags', []) %}
    <div style="background-color:white; border:thin solid grey; margin-left:95px; margin-right:6px">
    {% for tag in cell['metadata'].get('tags', []) %}
        &nbsp; <a href="https://{github_user_name}.github.io/{github_repo_name}/tag_index.html#{{ tag }}">{{ tag }}</a>
    {% endfor %}
    </div>
    {{ super() }}
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}

"""


def make_dir_if_needed(dir_name):
    """Create new directory if not present and verify that it exists."""
    if not os.path.exists(dir_name):
        print(f"- creating {dir_name} directory")
        os.mkdir(dir_name)
    else:
        print(f"- {dir_name} directory already exists")
    assert os.path.exists(dir_name), f"- failed to create directory {dir_name}"

def write_template_if_needed(template_content, templates_dir, template_filename):
    """Create template file if needed, and verify that it exists."""
    fname = os.path.join(templates_dir, template_filename)
    if not os.path.isfile(fname):
        with open(fname, 'w') as f:
            print(f"- writing {fname}")
            f.write(template_content)
    else:
        print(f"- {fname} already exists")

def nbsetup(config_file="nbpages.cfg"):
    """Setup directories if needed with default configuration and templates."""

    # nbpages default configuration
    templates_dir = "templates"
    figures_dir = "figures"
    data_dir = "data"
    src_dir = "notebooks"
    dst_dir = "docs"

    # verify a .git repository has been established
    assert os.path.exists('.git'), ".git subdirectory not found. "
    git_config = configparser.ConfigParser(strict=False)
    git_config.read(os.path.join(".git", "config"))
    github_repo_url = git_config['remote "origin"']['url']
    github_user_name = github_repo_url.rsplit('/')[-2]
    github_repo_name = github_repo_url.rsplit('/')[-1].split('.')[0]
    github_pages_url = f"https://{github_user_name}.github.io/{github_repo_name}"

    print(f"- creating {config_file} from .git/config")
    if os.path.isfile(config_file):
        config_file_backup = config_file + datetime.datetime.now().strftime(".backup-%Y%M%dT%H%M%S")
        print(f"- backing up {config_file} to {config_file_backup}")
        shutil.copy2(config_file, config_file_backup)

    config = configparser.ConfigParser()
    config["NBPAGES"] = {"github_repo_url": github_repo_url,
                         "github_user_name": github_user_name,
                         "github_repo_name": github_repo_name,
                         "github_pages_url": github_pages_url,
                         "templates_dir": templates_dir,
                         "figures_dir": figures_dir,
                         "data_dir": data_dir,
                         "src_dir": src_dir,
                         "dst_dir": dst_dir,
                         }
    with open(config_file, "w") as f:
        print("- writing " + config_file)
        config.write(f)

    # create directories if needed
    for dir in [src_dir, dst_dir, templates_dir, figures_dir, data_dir]:
        make_dir_if_needed(dir)

    # create templates
    write_template_if_needed(notebook_header_tpl, templates_dir, 'notebook_header.tpl')
    write_template_if_needed(index_md_tpl, templates_dir, 'index.md.tpl')
    write_template_if_needed(nbpages_tpl, templates_dir, 'nbpages.tpl')

    # create an initial index.md if none exists
    if "index.md" not in os.listdir(dst_dir):
        print(f"- writing index.md to {dst_dir}")
        with open(os.path.join(dst_dir, "index.md"), "w") as f:
            f.write(f"# {github_repo_name}\n")

    return 0


if __name__ == "__main__":
    sys.exit(nbsetup())