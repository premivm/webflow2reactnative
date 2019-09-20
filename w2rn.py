#! /usr/bin/env python3

import sys
import os
import generators
from bs4 import BeautifulSoup
from matcher import Matcher
from string import Template
from pathlib import Path


def process(tag, matchers, output, parent, styled_components):
    for m in matchers:
        if m.match(tag):
            return m.generate(tag, output, parent)

    return parent, styled_components


def processInputDir(input_dir, output_dir):
    for path in Path(input_dir).glob("*.html"):
        with open(path, "r") as infile:
            inp = BeautifulSoup(infile, "lxml")

        outp = BeautifulSoup("", "lxml")

        # find_all walks the tree in order and emits a list of all tags in the system,
        # so we don't need to process things recursively.
        styled_components = ''
        total_styled_components = ''
        div = outp.new_tag("View")
        for ch in inp.body.find_all(True):
            div, styled_components = process(
                ch, matchers, outp, div, styled_components)
            if styled_components not in total_styled_components:
                total_styled_components += styled_components

        outp.append(div)

        writeReactNativeFile(output_dir, path.name,
                             total_styled_components, outp)


def get_template():
    template = ''
    if '__file__' in vars():
        template = os.path.join(os.path.dirname(
            os.path.realpath('__file__')), 'templates', 'rn_view.template')
    else:
        template = os.path.join('templates', 'rn_view.template')

    with open(template, encoding='utf8') as f:
        template = f.read()
    return template


def writeReactNativeFile(output_dir, filename, total_styled_components, outp):
    views_dir = os.path.join(output_dir, 'src', 'ui', 'views')
    os.makedirs(views_dir, exist_ok=True)
    react_native_filename = filename.capitalize().rpartition('.html')[
        0] + 'View'

    template = Template(get_template())
    content = template.substitute(styled_components=total_styled_components,
                                  jsx=outp.prettify(formatter='html'))

    with open(os.path.join(views_dir, react_native_filename + '.js'), "w") as outfile:
        print(content, file=outfile)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 w2rn.py <input-dir> <output-dir>")
        exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # This is a list of all the matcher objects. Be aware that if multiple
    # Matchers match the same tag, only the first one that matches gets called.
    matchers = [
        Matcher("a", "class", "w-button",
                generators.gen_button, input_dir, output_dir, 0),
        Matcher("a", "class", "link",
                generators.gen_button, input_dir, output_dir, 0),
        Matcher("div", "class", "w-container",
                generators.gen_view, input_dir, output_dir, 0),
        Matcher("div", "class", "w-form",
                generators.gen_view, input_dir, output_dir, 0),
        Matcher("input", "class", "w-input",
                generators.gen_textinput, input_dir, output_dir, 0),
        Matcher("body", "class", "outercontainertop",
                generators.gen_view, input_dir, output_dir, 0),
        Matcher("h1", "class", "heading",
                generators.gen_text, input_dir, output_dir, 0),
    ]

    processInputDir(input_dir, output_dir)
