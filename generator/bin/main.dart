import 'package:generator/markdown.dart';
import 'package:generator/common.dart';
import 'package:generator/mustache.dart';
import 'package:generator/utils.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:shelf_static/shelf_static.dart';

main(List<String> args) async {
  final metadatas = await readMarkdown(MARKDOWN_DIR);
  await renderMustache(BUILD_DIR, metadatas);
  copyFiles(MARKDOWN_DIR, BUILD_DIR,
      except: {MARKDOWN_EXTENSION, MUSTACHE_EXTENSION});
  copyFiles(MUSTACHE_DIR, BUILD_DIR,
      except: {MARKDOWN_EXTENSION, MUSTACHE_EXTENSION});

  var handler = createStaticHandler(BUILD_DIR, defaultDocument: 'index.html');
  io.serve(handler, 'localhost', 8080);
  log('serve: http://localhost:8080');
}
