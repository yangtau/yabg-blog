---
title: Projects
author: τ
template: post
hide: true
---

## 大学期间的项目

### HBS
<a href="https://github.com/yangtau/hbs"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/hbs.svg"></a>
HBS 是我的本科毕业设计。
HBS 为 HBase 提供了 ACID 语义的事务支持。它使用 multi-version timestamp ordering 和 write-snapshot isolation 结合的并发控制算法，
两阶段提交的策略。理论上，HBS 应该具有非常好的可拓展性，同时提供了最高可串行化的隔离级别。论文：https://yangtau.me/achieved/undergraduate_thesis.pdf


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
但是 YABG 使用 Jinja2 配置页面模板，这使得它的拓展能力非常强大。
现在流行的博客生成器都太复杂了，我不能便捷地根据自己的需求修改，所以只好自己写一个。

### Feed the Dragon 游戏
<a href="https://github.com/yangtau/feed-the-dragon"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/feed-the-dragon.svg"></a>
一个软件工程课上写的游戏，使用 PyGame 开发，游戏 UI 使用了 Pygame GUI 库（当时这个库还很粗糙，我还给它贡献了几个 PR）。

### CSAPP
<a href="https://github.com/yangtau/csapp"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/csapp.svg"></a>
学习 CSAPP 这本书时所做的笔记和实验。实验部分收获很大，包括实现 malloc、HTTP 代理等。

### SMS
<a href="https://github.com/yangtau/SMS"><img style="margin:2px" src="https://gh-card.dev/repos/yangtau/SMS.svg"></a>
这个项目是一个学生管理系统的前后端的实现。由于当时正好迷恋 Dart 语言，就前后端都用了 Dart。
个人认为一些小的 WEB 应用用 Dart 开发还是挺不错的，独特的类型系统使得它既可以有很高的开发效率，同时又能有不错的可维护性和执行效率。
缺点是 Dart 目前主要寄生在 Flutter 身上，可用的第三方库并不多。
在这个项目中，我利用 Dart 的反射机制，开发了一个支持 MySQL 的 ORM 库。
