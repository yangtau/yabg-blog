
from jinja2 import FileSystemLoader, Template, Environment, select_autoescape
import yaml
import markdown
import os

pages_dir = "pages/"
templates_dir = "templates/"
output_dir = "./"
markdown_extension = ".md"
template_extension = ".j2"

global_metadata_user_value = 'τ'
global_metadata_domain_value = 'https://yangtau.me'
global_metadata_copy_right_year_value = '2019'
global_metadata_posts = 'posts'

# metadata of pages:
metadata_title = 'title'  # compulsive
metadata_template = 'template'  # default: post
metadata_template_deafult = 'post'
metadata_render = 'render'  # default: true
metadata_hide = 'hide'  # default: false
# for inner use
metadata_url = 'url'
metadata_content = 'content'
metadata_date = 'date'

build_int_metadata = (metadata_content, metadata_url,
                      metadata_hide, metadata_render,
                      metadata_template, metadata_title,
                      metadata_date
                      )


env = Environment(loader=FileSystemLoader(templates_dir),
                  autoescape=select_autoescape(['css']))


def get_template(template_name) -> Template:
    return env.get_template(template_name+template_extension)


def render_jinja(metadata, global_metadata):
    tpl = get_template(metadata[metadata_template])
    data = global_metadata.copy()
    # override the same key in global data using page metadata
    data.update(metadata)
    return tpl.render(data)


def list_files(dir_path) -> [str]:
    '''
    list relative paths all files in `dir_path` recursively
    '''
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


def get_html_url(file_path: str) -> str:
    '''
    change file path to html url
    eg, pages/hello.md -> hello.html
    '''
    path_rm_page_dir = '/'.join(file_path.split('/')[1:])
    return '.'.join(path_rm_page_dir.split('.')[:-1]) + '.html'


def render_markdown(file_path, global_metadata):
    print('processing %s...' % file_path, end='\t')
    with open(file_path, "r") as f:
        lines = f.readlines()
        # find yaml filed
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
        metadata = dict(yaml.load(''.join(lines[first+1:second])))
        # check metadata
        # url, content is not allowed for user to set
        # title is suggested
        if metadata_url in metadata:
            raise Exception('%s should not be setted by user' % metadata_url)
        if metadata_content in metadata:
            raise Exception('%s should not be setted by user' %
                            metadata_content)
        if metadata_title not in metadata:
            print("Warning: `%s` is strongly suggested!" % metadata_title)
        # default for some metadata: hide, render, template
        metadata.setdefault(metadata_hide, False)
        metadata.setdefault(metadata_render, True)
        metadata.setdefault(metadata_template, metadata_template_deafult)
        if metadata[metadata_hide]:
            print('hide is setted to be True')
            return
        metadata[metadata_url] = get_html_url(file_path)
        # add to global metadata before render content
        if metadata[metadata_template] == metadata_template_deafult:
            copy = metadata.copy()
            global_metadata[global_metadata_posts].append(copy)
            '''
            for example, a post has metadata: {'tag':['code', 'system']}
            then global metadate will be {...'tag':{'code':[], 'system':[]}...}
            '''
            for key, value in copy.items():
                if key not in build_int_metadata:
                    global_metadata.setdefault(key, {})
                    if isinstance(value, list):
                        for v in value:
                            global_metadata[key].setdefault(value, [])
                            global_metadata[key][value].append(copy)
                    else:
                        global_metadata[key].setdefault(value, [])
                        global_metadata[key][value].append(copy)

        # render `html` content
        content = ''.join(lines[second+1:])
        if metadata[metadata_render]:
            extras = ['markdown.extensions.toc'] if metadata[metadata_template] \
                == metadata_template_deafult else []
            extras += ['markdown.extensions.extra', ]
            html = markdown.markdown(content,
                                     extensions=extras)
            metadata[metadata_content] = html

        else:
            metadata[metadata_content] = content
    print('done')
    return metadata


def get_global_metadata() -> dict:
    return {global_metadata_posts: [],
            'user': global_metadata_user_value,
            'year': global_metadata_copy_right_year_value,
            'domain': global_metadata_domain_value
            }


def generate():
    rel_pages_dir = os.path.relpath(pages_dir)
    files = list_files(pages_dir)
    global_metadata = get_global_metadata()
    pages = []
    for f in files:
        if f.endswith(markdown_extension):
            pages.append(render_markdown(f, global_metadata))
        else:
            # copy to output dir directly
            out_file_path = os.path.join(
                output_dir, '/'.join(f.split('/')[1:]))
            with open(f, "rb") as file:
                copy_to_output(file, out_file_path)
    template_files = list_files(templates_dir)
    for f in template_files:
        if not f.endswith(template_extension):
            out_file_path = os.path.join(
                output_dir, '/'.join(f.split('/')[1:]))
            with open(f, "rb") as file:
                copy_to_output(file, out_file_path)
    # print(global_metadata)
    # for k, v in global_metadata.items():
    #     print(k)
    #     print(v)
    # print(global_metadata)
    for page in pages:
        render_res = render_jinja(page, global_metadata)
        with open(os.path.join(output_dir, page[metadata_url]), "w") as f:
            print("writing %s ...\t" % page[metadata_url])
            f.write(render_res)
            print('done')


if __name__ == "__main__":
    generate()
