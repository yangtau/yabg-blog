---
title: "Tail Call"
author: τ
date: 2021-06-22
template: post-code
---

## X86 Tail Call 汇编

阶乘的 C 语言实现（尾优化版本）：

```c
// fac.c
int __attribute__((noinline)) fac_iter(int n, int acc) {
  if (n <= 1)
    return acc;
  else
    return fac_iter(n - 1, acc * n);
}

int fac(int n) { return fac_iter(n, 1); }
```

代码中的 `__attribute__((noinline))` 是告诉编译器在 `fac` 中调用 `fac_iter` 时不要内联函数，以便观察 tail call 对应的汇编代码。

 clang 编译选项：

- `-mno-sse`: 关闭 SIMD 优化
- `-fno-asynchronous-unwind-tables`: 关闭 `.cfi`

### `-O0`

`clang -c -mno-sse -fno-asynchronous-unwind-tables -S -O0 fac.c` 的结果没有尾优化，所有的函数调用都是使用 `callq`：

```assembly
_fac_iter:                              ## @fac_iter
    movl    %esi, %eax
    cmpl    $2, %edi
    jl    LBB0_2
    pushq    %rbp
    movq    %rsp, %rbp
    imull    %edi, %eax
    decl    %edi
    movl    %eax, %esi
    callq    _fac_iter
    popq    %rbp
LBB0_2:
    retq

_fac:                                   ## @fac
    pushq    %rbp
    movq    %rsp, %rbp
    movl    $1, %esi
    callq    _fac_iter
    popq    %rbp
    retq
```

### `-O2`

`clang -c -mno-sse -fno-asynchronous-unwind-tables -S -O2 fac.c` 的结果已有尾优化：

```assembly
_fac_iter:                              ## @fac_iter
    pushq    %rbp
    movq    %rsp, %rbp
    movq    %rsi, %rax
    cmpq    $2, %rdi
    jl    LBB0_2
LBB0_1:                                 ## =>This Inner Loop Header: Depth=1
    imulq    %rdi, %rax
    leaq    -1(%rdi), %rcx
    cmpq    $2, %rdi
    movq    %rcx, %rdi
    jg    LBB0_1
LBB0_2:
    popq    %rbp
    retq

_fac:                                   ## @fac
    pushq    %rbp
    movq    %rsp, %rbp
    movl    $1, %esi
    popq    %rbp
    jmp    _fac_iter                       ## TAILCALL
```

在 `fac_iter` 对应的汇编代码中，递归函数调用被直接优化成了循环的实现。

而在 `fac` 函数中，我们可以看到调用 `fac_iter` 的地方使用的是 `jmp`，而不是 `callq`。`fac` 中首先把 `%esi` （也就是 `fac_iter` 的第二个参数）设置为 1，然后直接 jump 到 `fac_iter` 执行。这也意味着，`fac_iter` 函数栈帧之上的栈帧是调用 `fac` 的函数，而不是 `fac`。`fac_iter` 函数返回时，直接返回调用 `fac` 函数的地方，而不是 `fac` 内部。

Tail call 优化的好处在于可以节省栈空间，也为较深的调用链和尾递归提供了可能。

### Tail Call 优化的递归调用

值得注意的是，在上面的 `fac_iter` 的汇编中，尾递归并没有使用 tail call 的优化，而是直接优化成了函数内部的循环。事实上我们可以把 tail recursion 看做一种特殊的 tail call，它可以被优化成函数内部的循环，也可以使用一般的 tail call 优化。下面的代码是我从 `-O2` 的汇编代码修改而来，把 `fac_iter` 中的循环修改为 tail call：

```diff-assembly
_fac_iter:                              ## @fac_iter
    pushq    %rbp
    movq    %rsp, %rbp
    movq    %rsi, %rax
    cmpq    $2, %rdi
    jl    LBB0_2
+    imulq    %rdi, %rsi     ## %rsi *= %rdi (acc * n)
+    leaq    -1(%rdi), %rdi  ## %rdi -= 1    (n-1)
+    popq    %rbp
+    jmp     _fac_iter
LBB0_2:
    popq    %rbp
    retq
                                        ## -- End function
_fac:                                   ## @fac
    pushq    %rbp
    movq    %rsp, %rbp
    movl    $1, %esi
    popq    %rbp
    jmp    _fac_iter                       ## TAILCALL
```

如果简单分析汇编代码，我们可以发现，tail call 的版本不会因为递归调用产生新的栈帧，大致等价于循环。但是相比与普通的循环版本，tail call 版本中多了许多的对栈帧指针 `%rbp` 的操作。

### 性能比较

我们把上面三段代码分别编译并链接相同的测试代码，得到的程序分别称为 `fac-O0`、`fac-O2`、`fac-tail-call`。我使用的测试环境是 MacBook Pro (16-inch, 2019) Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz。测试结果如下（macrosconds）：

|            | `fac-O0` 时间  | `fac-O2` 时间 | `fac-tail-call` 时间 |
| :--------- | :------------- | :------------ | -------------------- |
| 5!         | 5              | 5             | 4                    |
| 10!        | 5              | 5             | 5                    |
| 100000!    | 2,703          | 117           | 142                  |
| 1000000!   | 29,670         | 1,032         | 1,385                |
| 10000000!  | stack overflow | 10,095        | 13,650               |
| 100000000! | -              | 84,169        | 103,362              |

可以看到，`fac-O2` 和 `fac-tail-call` 的性能相差不是特别明显，`fac-O2` 所用的时间大概是 `fac-tail-call` 的 80% 左右。

### 完整源码

<script src="https://gist.github.com/yangtau/8a3046562aeb1567f934e238d49c275a.js"></script>

