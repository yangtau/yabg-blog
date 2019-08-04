import 'dart:io';
import 'package:mustache/mustache.dart';
import 'common.dart';
import 'utils.dart';

String _getFileName(String path) {
  // print('here');
  final splitByDot = path.split('/').last.split('.');
  splitByDot.removeLast();
  return splitByDot.join('.');
}

Future<Map<String, Template>> _readMustaches(String dir) async {
  final files = await Directory(dir).list().toList();
  final templates = <String, Template>{};

  final resolver = (String name) {
    return templates[name];
  };

  for (var f in files)
    if (f.path.endsWith(MUSTACHE_EXTENSION))
      templates[_getFileName(f.path)] = Template(
          await File(f.path).readAsString(),
          partialResolver: resolver);
  log("build: read mustache done.");
  return templates;
}

renderMustache(String outputDir, List<Map> metadatas) async {
  final templates = await _readMustaches(MUSTACHE_DIR);
  for (final metadata in metadatas) {
    final tplName = TYPE_TO_TEMPLATE[metadata[METADATA_KEY_TYPE]];
    final tpl = templates[tplName];
    if (tpl == null) {
      throw Exception('No templates matchs type $tplName');
    }
    final rendered = tpl.renderString(metadata);
    File(outputDir + metadata[METADATA_KEY_URL]).writeAsString(rendered);
  }
  log("build: render mustache done.");
}

// main(List<String> args) async {
//   final data = {
//     "hello": [
//       {"world": 'a'},
//       {"world": 'b'}
//     ],
//     "title": "TITLE"
//   };
//   final templates = await _readMustaches('test/templates/');
//   print(templates['c'].renderString(data));
// }
