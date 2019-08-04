import 'dart:io';
import 'package:generator/markdown.dart';
import 'package:generator/common.dart';
import 'package:generator/mustache.dart';
import 'package:generator/utils.dart';

main(List<String> args) async {
  final metadatas = await readMarkdown(MARKDOWN_DIR);
  await renderMustache(BUILD_DIR, metadatas);
  copyFiles(MARKDOWN_DIR, BUILD_DIR,
      except: {MARKDOWN_EXTENSION, MUSTACHE_EXTENSION});
  copyFiles(MUSTACHE_DIR, BUILD_DIR,
      except: {MARKDOWN_EXTENSION, MUSTACHE_EXTENSION});
}
