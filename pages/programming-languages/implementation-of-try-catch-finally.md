---
title: try-catch-finally 异常处理的实现
date: 2020-06-18
template: post-code
author: τ
hide: true
---

*try-catch-finally* 是一种常见的异常处理范式，在众多常见编程语言中被采用，如 Java，JavaScript 等。本文会简单探讨其实现机制。

## 语义

要讲清楚 try-catch-finally 的实现，就必须先明确它的语义。

## 实现

- E: 异常栈
- push_e: 设置异常处理程序
- pop_e: 清楚异常处理程序

某段代码产生异常则会从 E 栈顶取出异常处理程序执行。如果 E 为空，则异常没有被捕获，输出异常信息，退出程序。

### try-catch-finally 语句的翻译

```
    jump try
catch_entry:
	#if has_catch
	reset_e
    push_e(finally)
    +-------------+
    | catch-block |
    +-------------+
    pop_e
    #endif // has_catch
    jump finally
try:
    push_e(catch_entry)
    +-------------+
    |  try-block  |
    +-------------+
    pop_e
finally:
	+-------------+
	|finally-block|
	+-------------+
	test_e
```

### 特殊情况

#### try-block，catch-block，finally-block 中有 break，continue 语句

先在 break 或 continue 之前冗余 finally 语句。需要注意的是嵌套异常处理中，外层的 finally 也可能被冗余进来。当前层的 finally 应该被外层异常处理程序处理，所以每次冗余 finally 之前都应该 pop_e。

```javascript
for (var i = 0; i < 2; i++) {
	try {
        console.log(i);
        throw 1; // enable catch
    } catch (e) {
        try {
            try {
                /*
                pop_e # the catch_entry is finally1
                finally1
                pop_e
                finally2
                pop_e
                finally3
                 */
                break;
            } finally { // finally1
                throw 'error1';
            }
        } finally { // finally2
            console.log(1);
            throw 'error2';
        }
    } finally { // finally3
        continue;
    }
}
```

```js
for (var i = 0; i < 2; i++) {
	try {
        console.log(i);
    } catch (e) {
    } finally { // finally3
        try {
            try {
                /*
                pop_e # the catch_entry is finally1
                finally1
                pop_e
                finally2
                # finally3 is not in the finalizer_stack
                 */
                break;
            } finally { // finally1
                throw 'error1';
            }
        } finally { // finally2
            console.log(1);
            throw 'error2';
        }
        continue;
    }
}
```

```js
for (var i = 0; i < 2; i++) {
	try {
        console.log(i);
    } catch (e) {
        try {
            try {
                /*
                pop_e # the catch_entry is catch
                # finally1 is null
                pop_e
                finally2
                pop_e
                finally3
                 */
                break;
            } catch(e) {
                console.log('oooops');
            }
        } finally { // finally2
            console.log(1);
            throw 'error2';
        }
    } finally { // finally3
        continue;
    }
}
```

finally 语句中的 break， continue，return 会 reset_e

#### return

try 语句中的 return 应该冗余所有外层 finally。
