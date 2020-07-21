---
title: τ
template: base
hide: true
---
## 项目

这是我大学期间做个的部分项目的一个简单介绍。

### Hedgehog
<a href="https://github.com/yangtau/hedgehog"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/hedgehog.svg"></a>
一门简单的脚本语言，是我为了学习编译相关知识而写的。我希望它有以下特性：简洁的语法，限制较为宽松的函数式编程范式，不错的性能，极高的编程效率。
目前仅仅实现了基础的功能，我将来会持续完善它。
这里有一篇博客介绍它的设计和实现的博客：[Hedgehog 的设计与实现](https://yangtau.me/programming-languages/design-and-implementation-of-hedgehog.html)。

### 单周期 MIPS CPU
<a href="https://github.com/yangtau/mips-cpu"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/mips-cpu.svg"></a>
支持大多数常用指令（大概有六十几条），可以运行 MIPS-GCC 编译出来的代码。实现了中断，可以用代码操作外设。

### MySQL 存储引擎
<a href="https://github.com/yangtau/example-engine"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/example-engine.svg"></a>
用 B+ 树实现的 MySQL 存储引擎。

### YABG
<a href="https://github.com/yangtau/yabg"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/yabg.svg"></a> 
一个静态博客网页生成器。相比与 Hexo 之类的应用，YABG 非常迷你，大概只有 200 行代码。
但是 YABG 可以 Jinja2 配置页面模板，使得它的拓展能力非常强大。
因为现在流行的博客生成器都太复杂了，我不能便捷地根据自己的需求修改，所以只好自己写一个。

### Feed the Dragon 游戏
<a href="https://github.com/yangtau/feed-the-dragon"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/feed-the-dragon.svg"></a>
一个软件工程课上写的游戏，使用 PyGame 开发，游戏 UI 使用了 Pygame GUI 库（当时这个库还很粗糙，我还给它贡献了几个 PR）。

### CSAPP
<a href="https://github.com/yangtau/csapp"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/csapp.svg"></a>
学习 CSAPP 这本书时所做的笔记和实验。实验部分收获很大，包括实现 malloc、HTTP 代理等。

### SMS
<a href="https://github.com/yangtau/SMS"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/SMS.svg"></a>
这个项目是一个学生管理系统的前后端的实现。由于当时正好迷恋 Dart 语言，就前后端都用了 Dart。
个人认为一些小的 WEB 应用用 Dart 开发还是挺不错的。独特的类型系统使得它既可以有很高的开发效率，同时又能有不错的可维护性和执行效率。
缺点是 Dart 目前主要寄生在 Flutter 身上，可用的第三方库并不多。
在这个项目中，我在利用 Dart 的反射机制，开发了一个支持 MySQL 的 ORM 库。

### UESTC 课表
<a href="https://github.com/yangtau/uestc"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/uestc.svg"></a>
成电课表 APP，使用 Flutter 开发，可以便捷查看课表和成绩。在安卓手机上可以用，IOS 没有测试过。
在我开发这个 APP 的过程中，学校教务处升级了网站，增强了反爬虫机制。由于精力有限（懒），我也没有更新爬虫。

