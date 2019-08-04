import 'dart:io';

// copy files like .css .js
copyFiles(String srcDirPath, String desDirPath,
    {Set except = const <String>{}}) async {
  final desDir = Directory(desDirPath);
  if (!await desDir.exists()) {
    await desDir.create();
  }
  Directory(srcDirPath).list().forEach((f) async {
    final path = f.path.replaceFirst(srcDirPath, desDirPath);
    if (await FileSystemEntity.isDirectory(f.path)) {
      copyFiles(f.path, path);
    } else {
      if (except.contains('.' + f.path.split('.').last)) return;
      File(f.path).copy(path);
    }
  });
}
