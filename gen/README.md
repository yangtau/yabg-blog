# Yet Another Blog Generator

*yabg* is a simple static blog generator built with [Jinja2](https://github.com/pallets/jinja) and [Python-Markdown](https://github.com/Python-Markdown/markdown).
I use it to power my blog. Most blog generators, like hexo, are too complex.
I just want a simple one without too many useless functions, so I build this one.
**example**: [yangtau.me](https://yangtau.me)

## Requirements

```bash
pip install Jinja2
pip install markdown
pip install pymdown-extensions
pip install PyYAML
```

## Config

- [ ] TODO

## Build

```bash
python3 yabg/main.py config.yaml
```

## [now.sh](now.sh) Deployment

```
FRAMEWORK PRESET: other
BUILD COMMAND: python3 -m pip install PyYAML && python3 -m pip install Jinja2 && python3 -m pip install markdown && python3 -m pip install pymdown-extensions && python3 yabg/main.py
OUTPUT DICTORY: public # setted in your config.yaml
```

# Dart-Generator

I first built this generator using Dart and Mustache, but the markdown library of Dart just supports the basic markdown syntax and Mustache is not powerful enough.

The code of Dart-Generator is on the branch [dart-gen](https://github.com/yangtau/static-blog-generator/tree/dart-gen).
