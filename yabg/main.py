#!/usr/bin/env python3
from jinja2 import FileSystemLoader, Environment
import yaml
import markdown
import os
import sys
import datetime

'''metadata'''
METADATA_TITLE = 'title'  # compulsive
METADATA_TEMPLATE = 'template'  # default: post
METADATA_TEMPLATE_DEAFULT = 'post'  # post.j2
METADATA_RENDER = 'render'  # default: true
METADATA_DATE = 'date'
'''invisable metadata'''
METADATA_URL = '__url'
METADATA_CONTENT = '__content'
METADATA_POSTS = '__posts'  # used for global access

'''markdown extensions'''
MARKDOWN_EXTS = ['markdown.extensions.extra',
                 'pymdownx.keys',
                 'pymdownx.mark',
                 'pymdownx.tilde',
                 'markdown.extensions.toc',
                 'pymdownx.magiclink',
                 'pymdownx.tasklist',
                 ]

'''config'''
TEMPLATE_DIR = 'template_dir'
PAGE_DIR = 'page_dir'
OUTPUT_DIR = 'output_dir'
STYLE_DIR = 'style_dir'

'''
Jinja
'''


def get_jinja2_env(templates_dir):
    return Environment(loader=FileSystemLoader(templates_dir))


def render_jinja(metadata, env):
    tpl = env.get_template(metadata[METADATA_TEMPLATE]+'.j2')
    return tpl.render(metadata)


def render_index(metadata, env, pages: list):
    tpl = env.get_template(metadata[METADATA_TEMPLATE]+'.j2')
    return tpl.render(metadata)


'''
file
'''


def list_files(dir_path) -> [str]:
    '''list relative paths all files in `dir_path` recursively'''
    xs = os.listdir(dir_path)
    res = []
    for f in xs:
        f_path = os.path.join(dir_path, f)
        if os.path.isfile(f_path):
            res.append(os.path.relpath(f_path))
        elif os.path.isdir(f_path):
            res.extend(list_files(f_path))
    return res


def copy_to_output(file, file_name):
    dir_path, _ = os.path.split(file_name)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_name, "wb") as f:
        f.write(file.read())


'''
markdown
'''


def split_markdown(lines: [str]) -> ([str], [str]):
    '''return the lines of metadata and the lines of markdown content'''
    first, second = -1, -1
    for k in range(len(lines)):
        if lines[k] == '---\n':
            if first == -1:
                first = k
            else:
                second = k
                break
    else:
        raise Exception('No metadata found in markdown file.')
    return (lines[first+1:second], lines[second+1:])


def get_page_metadata(lines: [str]) -> dict:
    metadata = dict(yaml.load(''.join(lines), Loader=yaml.SafeLoader))
    # check metadata
    # url, content is not allowed for user to set
    if METADATA_URL in metadata:
        raise Exception('%s should not be setted by user' % METADATA_URL)
    if METADATA_CONTENT in metadata:
        raise Exception('%s should not be setted by user' % METADATA_CONTENT)
    # title is suggested
    if METADATA_TITLE not in metadata:
        print("Warning: `%s` is strongly suggested!" % METADATA_TITLE)
    # default for some metadata: render, template
    metadata.setdefault(METADATA_RENDER, True)
    metadata.setdefault(METADATA_TEMPLATE, METADATA_TEMPLATE_DEAFULT)
    metadata.setdefault(METADATA_DATE, datetime.date.today())
    return metadata


def render_markdown(file_path) -> dict:
    print('markdown: processing %s...' % file_path)
    with open(file_path, "r") as f:
        lines = f.readlines()
    metadatalines, content_lines = split_markdown(lines)
    content = ''.join(content_lines)
    metadata = get_page_metadata(metadatalines)
    if metadata[METADATA_RENDER]:
        html = markdown.markdown(content, extensions=MARKDOWN_EXTS)
        metadata[METADATA_CONTENT] = html
    else:
        metadata[METADATA_CONTENT] = content
    return metadata


def load_config(config_file: str):
    with open(config_file) as f:
        lines = f.readlines()
    return dict(yaml.load(''.join(lines), Loader=yaml.SafeLoader))


def gen_site_map(config, urls):
    filename = os.path.join(config[OUTPUT_DIR], config['sitemap'])
    urls = [os.path.join(config['domain'], u)+'\n' for u in urls]
    with open(filename, "w") as f:
        f.writelines(urls)


def generate(config_file: str):
    config = load_config(config_file)
    # change to the dir containing the config_file, because all paths in config
    # are relative paths with respect to config_file.
    config_dir = os.path.dirname(config_file)
    if config_dir != '':
        os.chdir(config_dir)

    pages_dir = os.path.relpath(config[PAGE_DIR])
    output_dir = os.path.relpath(config[OUTPUT_DIR])
    files = list_files(pages_dir)
    pages = []
    for f in files:
        if f.endswith('.md'):
            md = render_markdown(f)
            url = f.replace(pages_dir+'/', '')
            if md[METADATA_RENDER]:
                md[METADATA_URL] = url[:-2]+'html'
                md[METADATA_POSTS] = pages
            else:
                md[METADATA_URL] = url
            pages.append(md)
            continue
        # copy to output dir directly
        out_file = os.path.join(output_dir, f.replace(pages_dir+'/', ''))
        print('copying %s to %s...' % (f, out_file))
        with open(f, "rb") as file:
            copy_to_output(file, out_file)
    # render pages with j2
    j2_env = get_jinja2_env(config[TEMPLATE_DIR])
    for page in pages:
        print('jinja2: rendering %s...' % page[METADATA_URL])
        render_res = render_jinja(
            page, j2_env) if page[METADATA_RENDER] else page[METADATA_CONTENT]
        file_name = os.path.join(output_dir, page[METADATA_URL])
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "w") as f:
            f.write(render_res)
    # generate sitemap
    gen_site_map(config, [md[METADATA_URL] for md in pages])
    # copy style files
    style_dir = os.path.relpath(config[STYLE_DIR])
    files = list_files(style_dir)
    for filename in files:
        out = os.path.join(output_dir, filename.replace(style_dir+'/', ''))
        print('copying %s to %s...' % (filename, out))
        with open(filename, 'rb') as f:
            copy_to_output(f, out)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        config_file = sys.argv[1]
    else:
        config_file = './config.yaml'
    if not os.path.exists(config_file):
        print('No config file was found in current dir and no filename of config are indicate.')
        print('Usage: %s [config_file]' % sys.argv[0])
        print('Or you should include a file named `config.yaml` in current dir')
        exit()
    generate(config_file)
