---
title: Hedgehog 的设计与实现
date: 2020-07-04
template: post-code
author: τ
---

Hedgehog 是我在编译课上完成的一门编程语言, 其目的是学习编译原理相关知识。它语法简洁，动态类型，内置 List，Map 等常用数据结构，运行在栈式虚拟机上。本文将简单介绍这门玩具式的编程语言，以及我在设计实现它的过程中的一些思考。它的源码开源在了 Github 上： [hedgehog](https://github.com/yangtau/hedgehog)，欢迎 star、fork 和提 issue。

[TOC]

## 前言

Hedgehog 的设计目标是一门像 Python，Ruby 那样容易上手，语法简单，编程效率高，功能足够强大的脚步语言。首先它的定位是一门脚步语言，目的是能够快速编写帮助程序员处理琐事的代码。这意味着它的表达能力要足够强大，能用一句简单的话就能表达复杂的语义。其次它应该是动态类型的，让用户在编写逻辑功能的时候不会受限于具体的类型。它还应是高效的，高效指的是代码编写的效率而非代码执行的效率。过去（现在也是），我们常常容易将目光局限于运行的高效，但是编写代码的高效常常被忽视。然而，如果一门语言能够在编写代码上做到高效，意味着程序员能够将部分繁琐的工作快速地表示成为代码，也能够高效为已有系统添加功能。这也是为什么 Python 这门执行效率并不高的语言能够如此受欢迎的原因。

但是 Python，Ruby 两门语言中也有一些设计上的遗憾。例如 Python 虽然号称支持多范式编程，但是它对函数式编程的支持相当鸡肋。例如这样的代码 `list(map(lambda x: x*x, [1, 2, 3]))`, 由于语法的限制，Python 的匿名函数只能写在一行，不能过于复杂。同时像 `map`，`reduce` 这些高阶函数在 Python 的实现中少了函数式本身的优雅，更像是将函数式编程强行加在了面向对象的语言中。上面那行代码在 Python 中更加常用的写法是 `[x*x for x in [1, 2, 3]]`，看起来优雅了不少，但是表达能力上也弱了很多。而 Ruby 在这方面显然做得更加出色，在 Ruby 中我们会这样写 `[1, 2, 3].map {|x| x*x}`。这个例子相对简单，三个写法看起来没有特别大的差别。但是处理更加复杂的逻辑的时候，Ruby 会更加游刃有余。

Ruby 在我心中已经相当出色了。但是它最大的问题是执行效率非常低，这也使得它没能被更加广泛地应用。它最初的执行方式是直接执行语法树，在后面的版本中改进为了在栈式虚拟机上执行。不过，这并没有根本性地改变现状。Ruby 复杂的语法设计（用 YACC 描述的语法文件有上万行），还有复杂的语义，让 Ruby 拥有极强表达能力的同时也为性能优化埋下了祸根。

Hedgehog 在设计实现中，会尽量多地去吸收 Python 和 Ruby 的优点，同时避免两者设计上的缺憾。目前 Hedgehog 仍然处于初级阶段，还在实现一些最最基础的功能。之后我会继续探索如何去完成我的设计目标。

### 已实现的功能

- 类型：整数，浮点数，字符串，数组，字典（hash 表）。
- 全局变量与局部变量
- 控制结构：*if* & *while*
- 函数

### 计划之中的功能

- [ ] 闭包
- [x] 垃圾回收
- [ ] 高阶函数 (map, reduce, filter 等)
- [ ] 用户自定义类型
- [ ] 标准库（内置数据结构相关库，文件读写库，网络库）


## 使用

下面简单说明如何编译、使用 Hedgehog。

**环境要求：**

- GCC
- bison & flex

**编译：**

首先从 Github 上下载或者克隆项目，然后编译。

```bash
git clone https://github.com/yangtau/hedgehog.git
cd hedgehog
make
```

**运行：**

之后在 src 目录下会生成名为 hg 的可执行文件，它接受一个文件名字符串作为输入，然后执行该文件。

```
./src/hg examples/test.hg
```

examples 目录下有一些 Hedgehog 程序文件，可以使用编译出的 hg 文件去执行测试。

## 设计

### 语法设计

一门编程语言的语法（我这里说的语法包含了它的词法），很大程度上决定了它的使用体验。在设计 Hedgehog 的语法的时候，我参考了很多 Rust、Ruby 的设计，同时也按照自己的想法做出了改进。具体的语法细节可以在 `src/parse.y` 文件中查看，我这里更想谈两个小细节上的设计。

#### 表达式分割符

在很多编程语言中，表达式结束符一般是 `;`。例如 C 语言每条语句后必须加 `;`。而为了让语法更加简洁，我选择了 Python、Ruby 的方案，即用换行符来分割表达式。但是这一设计带来了很多的问题。例如下面这个例子：

```js
let a = c +
        b
puts(a)
```

如果粗暴地使用换行符来分割语句，那么上述代码在语法解析过程中就应该报错。但是这样的写法应当是符合人类的习惯的，在一条语句过长的时候，我们也常常会分割成两行来写。解决这个问题的方法是在词法解析的时候忽略 `+` 后面的换行符，用 Lex 实现如下：

```lex
TRAIL  ([\t \n]|"#"[^\n]*"\n")*
%%
"+"{TRAIL}                      LEX_RETURN(op_add);
...
```

不过这需要相当谨慎，不是所有的符号都会忽略其后的换行符，在忽略换行符的时候要非常谨慎。

例如下面的代码：

```js
let d = a
		+ c
```

这到底是两条语句，还是一条呢？一个变量符号不应该忽略其后的换行符，所以应当是两条语句。
但是，第二行的 `+` 没有语义上的意义，容许这样的写法容易产生歧义，让代码更加不可读。而且出现这样的写法多半是程序员的失误。

还有其他一些小细节值得考虑，例如多个连在一起的换行符。显然不是每一个换行都对应着一条语句。可能是多对一的情况。还有一种可能在文件结尾根本就没有换行符，但是最后一条语句还是应当被解析。

关于这个问题，JS 的处理非常有趣。JS 中表示语句结束的 `;` 是可选的，它会在预处理的过程中在每行代码的末尾自动加上 `;`。
这样的做法太容易导致 bug 了，举个例子:
```js
label:
for (var j=0; j < 3; j++) {
  for (var i=0; i < 20; i++) {
    if (i == 10) {
      console.log('i=10')
      break label
    }
  }
}
```
```js
label:
for (var j=0; j < 3; j++) {
  for (var i=0; i < 20; i++) {
    if (i == 10) {
      console.log('i=10')
      break 
      label
    }
  }
}
```
第一段代码会输出一行，而第二段代码输出会三行。原因是第二段代码中 `break` 语句末尾自动加上 `;` 而忽略了其后的 `label`。
所以一般 JS 的代码规范中都会要求语句结束写 `;`。

一门动态类型的语言在语义上的检查本来就很弱了，如果在语法上也放松要求、容许一些程序员显然的错误，就变成了 bug 的温床。
JS 这样的设计真是得不偿失啊。

总之，想要完美地去掉 `;` 真不是一件容易的事啊。我目前的想法是：`+` 这种二元操作符显然不能作为语句的结束，就忽略其后的换行符。
而对于 `+` 写在语句开头这种情况就输出警告信息提醒程序员(因为这种写法虽然没有意义，但是在语法层面上是没有问题的)。

#### 没有括号的函数调用

在很多函数式编程语言中函数调用的括号是可以不要的，例如 Haskell：

```haskell
Prelude> let add x y = x+y
Prelude> add 3 4
7
```

`add` 函数在定义和调用过程中都没有用到括号。

首先说说这样做的好处：

1. 将函数和普通的数据统一其他。事实上，在 Haskell 中几乎一切都是函数: 变量 `x` 可以视为调用一个名为 `x` 的函数(它没有参数)，它会返回某个固定的值。常量 `3` 可以视为调用一个没有参数返回值为 3 的函数。这样的设计让编程语言在抽象层面可以做得更加纯粹。
2. 语法更加简洁。省略了括号、分割参数使用的逗号。

坏处也是很明显的：

1. 代码可读性降低。省略了括号事实上使得函数调用更加不那么明显。
2. 语义上的歧义。在有的情况下很难分清到底是取值还是函数调用，需要对语法做出更加多的限制。例如 `fn -1`， 到底是 `fn` 减去 `1`，还是 `fn(-1)` 呢？在 Haskell 中是前者， 因为 `-` 的优先级要高于函数调用。而要表代后者的语义，需要写成 `fn (-1)`。还有的语言是通过 `-` 号后是否有空格来区分的，例如 F# 和 Ruby。
3. 语法分析的实现更加困难复杂。

各种优劣权衡之下，我还是放弃了这个设计。

### 类型

目前 Hedgehog 内置整数，浮点数，布尔值，空值，字符串，列表（List），字典 （Map）类型。后续会加入对用户自定义类型的支持，目前的想法是用户自定义类型就是一个字典类型的语法糖，类似于 
 JS 那样。或者是一个 Tuple，这可能需要在编译的时候决定更多，不那么动态。

目前的整数底层直接使用 `int64_t` 实现，后期会考虑 Python 那种不限制大小的整数实现。

```js
# 整数
let a = 100
puts(a)
# 浮点数
let b = 10.98737
puts(b)
# boolean
let c, d = true, false # true, false
puts(c, d)
# nothing
let nil = () # 相当于别的语言中的 NULL，Nil 或者 None，受启发自 Rust
puts(nil)
# list, 一个 list 中可以存不同类型的数据
let xs = [a, b, c, d, nil] # 使用 [] 语法糖创建 List
let ys = List(nil, d, c, b, a) # 使用函数创建 List（注意：List 只是一个内置函数，而非 class 或者 type）
puts("xs =", xs)
puts("ys =", ys)
# map
let dict = {"age": 22,
            "name": "yangtau",
            "email": "yangtau@mail.com",
            "height": 199.99
           }
puts(dict)
```

### 程序控制结构

目前支持 *if-else*, *while* 两种基本的控制结构。后续会使用 map，reduce，filter 等高阶函数，还有模式匹配来替代传统的控制结构。*if-else*, *while* 的语法和 Rust 语言很相似，条件语句不需要加括号，程序块必须被包围在花括号内部。这里之所以没有引入 *for* 语句，是因为 *while* 完全足以代替它。而且后期引入了函数式的高阶函数，就更加希望它的使用者能够直接用 `map`, `reduce` 之类的操作。

```js
# if-else
let a = 100
if a >= 10*10 {
	puts("a >= 10*10")
} else if a < 1000 {
	puts("a < 1000")
} else {
	puts("no idea")
}

# while
let i = 0
while i < 10 {
    puts(i*i+i)
    i = i+1
}

# sort
def sort(ys, len) {
  let i = 0
  while i < len {
    let j = 0
    while j < len-i-1 {
      if ys[j] > ys[j+1] {
        ys[j], ys[j+1] = ys[j+1], ys[j]
      }
      j = j+1
    }
    i = i+1
  }
}

let ys  = [100, 102, 30, 50, 900, 5, 9, 10, 4, 2]
puts("before sort, ys =", ys)
sort(ys, 10)
puts("after sort, ys =", ys)
```

### 函数

使用 `def` 关键词可以定义函数，函数名后是参数列表。后续将考虑修改函数的语法，使用 let 关键字定义函数，并加入对闭包、匿名函数的支持。

下面是一段用递归的方式求值斐波拉契数列的程序。

```js
def fib(x) {
    if x == 0 {
        return 0
    } else if x == 1 {
        return 1
    } else {
        return fib(x-1)+fib(x-2)
    }
}

let i = 0
while i < 20 {
    puts(fib(i))
    i = i+1
}
```

## 实现

### 虚拟机的实现

Hedgehog 目前的虚拟机是栈式的，它没有真实世界中 CPU 的寄存器。运算所需的数据和产生的数据都保存在了一个栈上。栈式虚拟机最大的好处是便于代码编译，坏处是性能可能不如寄存器式虚拟机。

虚拟机目前支持下面这些指令：

```c
enum opcode {
    // 特殊常量:
    OP_NIL,
    OP_TRUE,
    OP_FALSE,
    // 运算:
    OP_EQUAL,
    OP_GREATER,
    OP_LESS,
    OP_GREATER_EQUAL,
    OP_LESS_EQUAL,
    OP_ADD,
    OP_SUBTRACT,
    OP_MULTIPLY,
    OP_DIVIDE,
    OP_MODULO,
    OP_NOT,
    OP_NEGATE,
    // VM 相关:
    OP_QUIT, // normally quit the VM
    OP_NOP,
    OP_POP, // pop 求值栈
    // 数据相关:
    OP_GET_CONST,
    OP_SET_STATIC,
    OP_GET_STATIC,
    OP_GET_LOCAL,
    OP_SET_LOCAL,
    // 跳转:
    OP_JUMP,
    OP_JUMP_IF_FALSE,
    OP_JUMP_BACK,
    // 函数：
    OP_CALL,
    OP_RET,
    OP_RETV,
};
```

可以看到，除了运算相关的指令，其他指令是相当少的。较少的指令数目使得 VM 的实现变得比较简单。

### 数据分区

```c
struct chunk {
    struct value_array statics; // global variables area
    struct value_array consts;  // constants area
    struct {
        size_t len;
        size_t capacity;
        struct hg_function* funcs;
    } funcs;
    uint8_t* code;
    size_t len;
    size_t capacity;
};

```

*chunk* 是保存编译结果的数据结构，可以看到上面有两个 `value_array` 用以存放数据， `code` 用以存放代码。

程序数据被分为 *static* , *const*, *local* 三种，对应执行中相关的 `SET`，`GET` 指令可以操作不同数据区的数据。

- *const* 是常量数据，只能读不能写。如 `let a =  3 + 100` 中 3 和 100 就存在常量数据区。
- *static* 是静态数据，可以读写，用以存放全局变量。
- *local* 是局部数据，可以读写，存放在栈中。

`static` 算是我前期实现上的一个缺陷，其实它完全可以用最低一层的 *local* 去代替。在命令行执行的模式下，维护一个哈希表记录全局变量和它在栈中对应位置即可。在后期的改进中，我会考虑去掉 `statics`。同时，函数被当做一种数据的时候， 对函数的引用也应该是运行时创建的，并且存在数据区。

### 数据的表示

```c
struct hg_value {
    enum hg_value_type type;
    union {
        bool _bool;
        int64_t _int;
        double _float;
        struct hg_object* _obj;
    } as;
};
```

Hedgehog 中所有数据都表示为这样一个结构体，通过 type 字段判定类型，然后再用 `as.__` 去访问。当对数组做操作的时候，会通过 *switch* 或者 *if-else* 语句去区分不同的类型。对于动态语言来说，这样的类型判定似乎是很难避免的。我也有考虑过实现像 Haskell 那样强大的类型推断的功能。不过考虑到类型推断让编译阶段的复杂度和编译时间大大增加就放弃了。

另外一个问题是 *hg_value* 这个结构体一般会占用 16 bytes 的内存空间，而表示数据本身其实最多只需要 8 bytes。需要专门用 8 bytes 来存类型实在是太浪费了。可以采用的一个优化方案是 NaN Boxing。在计算机中 64 位的浮点数分成符号位（1位），指数（11位），和尾数（52位）。当指数部分全为 1，而尾数部分不全为 1 时表示 NaN (Not a Number)。NaN 事实上有很多种可能（2^52^-1 种，实在是浪费），我们可以利用尾数的前 4 位表示类型，后面的 48 位表示各种数据。之所以后面剩余 48 位，是因为 64 位 Linux 下指针有效的位数为 后 48 位。但是这样做的可移植性可能不太好，因为其他系统中也只用 48 位表示地址吗？显然不一定。

### 控制结构的翻译

*if*，*while* 语句的编译是稍微有难度一点的部分。其中 *if-else* 的翻译如下:

```
/* IF-ELSE-IF-ELSE:
 *     if-condition
 * +---jump-if-false
 * |   if-block
 * |   jump  ------------+
 * +-->else-if-condition |
 * +---jump-if-false     |
 * |   else-if-block     |
 * |   jump  ------------+
 * +-->else-block        |
 *           <-----------+
 */
```

最大的困难点在于跳转指令跳转位置不是产生该指令的时候能够决定的，所以需要预留跳转地址、记录位置，然后再在跳转位置确定后再去填充。*while* 语句的翻译类似，就不再展示了。

一个有趣的现象是很多人都误认为 *jump if true* 和 *jump if false* 可以达到相同的效果，无非是翻译的逻辑变了而已。事实上，*jump if false* 常常能够用更少的指令数目去实现 *jump if true* 想要做到的事。

### 函数的实现

首先需要介绍运行时栈帧：
```c
struct frame {
    uint8_t* rt_addr;
    struct hg_value* slot; // 通过 slot 索引局部变量
};

struct vm {
    struct chunk* chk;
    uint8_t* ip;
    struct frame* frame_top;
    struct hg_value* stack_top;
    struct hg_value stack[STACK_SIZE];
    struct frame frames[FRAME_SIZE];
};
```

这里栈帧只保存两个值——返回地址和求值栈的栈顶指针（也就是函数使用的运行栈的开始位置，类似于 x86 的 rbp 寄存器）。在遇到 CALL 指令的时候，会将 ip 指向函数的开始地址，同时设置新的 frame，具体实现的 C 语言代码如下（省略了部分代码）：

```c
void call(struct vm* vm, struct hg_function func, int argc) {
    vm->frame_top++;

    *vm->frame_top = (struct frame){
        .rt_addr = vm->ip,
        .slot    = vm->stack_top - argc, // 把参数包围在调用的函数的栈帧之中
    };

    vm->ip = func->addr;
}
```

需要说明的是传参的部分。在调用函数时，会先将所有参数倒叙（从右至左）压到栈中，然后再执行 CALL 指令。这时 `stack_top` 指向第一个参数下面的位置，要让新的栈帧能够使用参数，需要让 `slot = stack_top - argument_count` 。这样在函数中就能够通过 `slot` 使用参数，例如 `slot[0]` 就是第一个参数（如果有参数）。

## 结语

Hedgehog 目前还仅仅处于开始的阶段，还在实现基本的功能，不过，我已经从其中受益匪浅。我想我以后会继续完善它，优化它，让它达到真正能够使用的地步。
