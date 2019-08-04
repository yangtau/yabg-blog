import 'package:markdown/markdown.dart';
import 'package:yaml/yaml.dart';
import 'dart:io';
import 'common.dart';
import 'utils.dart';
/*
format of header of markdown

---
type: 
title:
author:
date:
category:
`custom`:
---
`type` required, others are optional. 
Howerver, title, author and date is recommended.
*/

_readMetadata(String content) {
  final splited = content.split(METADATA_SEARATOR);
  if (splited.length < 3 || splited[0] != '' || splited[1] == '') return null;
  final yamlStr = splited[1];
  final yaml = loadYaml(yamlStr);
  if (yaml is! Map) {
    throw ('unexpected metadata');
  }
  var metadata = Map<String, dynamic>.from(yaml);
  if (!metadata.containsKey(METADATA_KEY_TYPE)) {
    throw ('metadata of markdown must contains `type`');
  }
  metadata[METADATA_KEY_HTML_CONTENT] = markdownToHtml(
      splited.sublist(2).join(METADATA_SEARATOR),
      extensionSet: ExtensionSet.gitHubFlavored);
  return metadata;
}

_getHtmlPath(String path) {
  // remove web
  final splitByDot = path.split('/').sublist(1).join('/').split('.');
  splitByDot.removeLast();
  return splitByDot.join('.') + HTML_EXTENSION;
}

Future<List<Map>> readMarkdown(String dirName) async {
  final metadatas = <Map>[];
  var indexMetadata = null;
  // final categoryMetadatas = [];
  await for (var f in Directory(dirName).list()) {
    if (!f.path.endsWith(MARKDOWN_EXTENSION)) continue;
    final markdownStr = await File(f.path).readAsString();
    final meta = _readMetadata(markdownStr);
    meta[METADATA_KEY_URL] = _getHtmlPath(f.path);
    metadatas.add(meta);
    if (meta[METADATA_KEY_TYPE] == METADATA_TYPE_INDEX) {
      indexMetadata = meta;
    }
    // if (meta[METADATA_KEY_TYPE] == METADATA_TYPE_CATEGORY) {
    //   categoryMetadatas.add(meta);
    // }
  }

  if (indexMetadata != null) {
    indexMetadata[METADATA_KEY_ARTICLES] =
        metadatas.where((m) => m[METADATA_KEY_TYPE] == METADATA_TYPE_ARTICLE);
  }
  log("build: markdown done.");
  return metadatas;
}
