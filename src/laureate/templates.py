from textwrap import dedent

from jinja2 import Environment, BaseLoader

from .util import dash_to_studly


env = Environment(loader=BaseLoader, trim_blocks=True)
env.filters["dash_to_studly"] = dash_to_studly


FORMULA_TEMPLATE = env.from_string(dedent("""\
    class {{ package.name|dash_to_studly }} < Formula
      include Language::Python::Virtualenv

      desc "{{ package.description }}"
      homepage "{{ package.homepage }}"
      url "{{ package.url }}"
      sha256 "{{ package.checksum }}"

      depends_on "{{ package.python }}"

    {% if resources %}
    {%   for resource in resources %}
      resource "{{ resource.name }}" do
        url "{{ resource.url }}"
        sha256 "{{ resource.checksum }}"
      end
      
    {%  endfor %}
    {% endif %}
    
      def install
    {% if python == "python3" %}
        virtualenv_create(libexec, "python3")
    {% endif %}
        virtualenv_install_with_resources
      end

      test do
        false
      end
    end
    """))


RESOURCE_TEMPLATE = env.from_string("""\
  resource "{{ resource.name }}" do
    url "{{ resource.url }}"
    sha256 "{{ resource.checksum }}"
  end
""")
