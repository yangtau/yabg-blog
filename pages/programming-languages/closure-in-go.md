---
title: "Golang Closure 的实现"
author: τ
date: 2022-02-14
template: post-code
---

> 文中使用的 golang 版本：`go1.16.10 darwin/amd64`

Go 语言对 closure 的支持比较完善，我们可以利用 closure 的能力来实现一些非常有趣的功能，本文会简单地分析一下 closure 在 go 语言中的实现。

例如下面的代码，`NewCounter` 会返回对一个 int 值加 1 的 closure。

```go
package closures

func NewCounter(init int) func() int {
    var a int = init
    return func() int {
        a++
        return a
    }
}

// c := NewCounter(0) 
// _ = c()
```

这里的函数内的局部变量 `a` 在 `NewCounter` 函数执行结束后并没有消失，我们可以调用返回的 closure `c` 来继续修改 `a`。这就是 closure 特殊的本领。

我们可以自然地想到两个问题：

1. 被 closure 用到的变量内存是怎么分配的（显然不能简单地应用局部变量就分配在栈上的简单规则了）？
2. closure 是怎么被调用的，它使用的外部的变量（上例中的 `a`）是怎么传递给它的？

如果 `NewCounter` 中没有 closure，那么变量 `a` 的生命周期在函数执行到 return 的时候就结束了。因为 closure 的存在，编译器会特殊处理 `a`，让它在 `NewCounter` 结束后还继续存活。这样的局部变量就到堆上分配内存空间，以便在声明它的函数执行结束之后，外部还能够访问到它。

但是并非所有被 closure 引用的变量生命周期都会拓展、都需要在堆上分配内存。例如下面的例子，`res` 被 `add4` 使用了，但是 `res` 就只会分配在栈上。这是因为在 `Foo` 执行结束后，程序就不可能用别的（正常的）方式访问到变量 `res` 了。

```go
package closures

func Bar(n int) int {
	var res int = 0
	add4 := func() {
		res = n + 4
	}
	add4()
	return res
}
```

如果一个变量被 closure 使用到了，这个变量会被称为 **closed variable**。go 语言的编译器首先会判断 closed variable 的捕获方式—— **captured by reference** 或者 **captured by value**；再应用逃逸分析决定变量内存分配的方式。

判断 captured by value 的条件是：

- 占用内存大小小于 128 bytes
- 被捕获后不会被重新赋值

逃逸分析就更加复杂了，需要对 AST 应用[数据流分析](https://en.wikipedia.org/wiki/Data-flow_analysis)，这里不详细展开细节了。

go 编译器自带了一些非常实用的功能，我们即使不了解具体规则也能知道变量的捕获方式和是否逃逸到堆上。我们可以使用命令 `go tool compile -l -m -m [filename]` 来输出相关信息。

例如对于上面第一个代码片段，我们可以得到下面的输出：

```
$ go tool compile -l -m -m foo.go
foo.go:6:3: NewCounter.func1 capturing by ref: a (addr=true assign=true width=8)
foo.go:5:9: func literal escapes to heap:
foo.go:5:9:   flow: ~r1 = &{storage for func literal}:
foo.go:5:9:     from func literal (spill) at foo.go:5:9
foo.go:5:9:     from return func literal (return) at foo.go:5:2
foo.go:4:6: a escapes to heap:
foo.go:4:6:   flow: {storage for func literal} = &a:
foo.go:4:6:     from func literal (captured by a closure) at foo.go:5:9
foo.go:4:6:     from a (reference) at foo.go:6:3
foo.go:4:6: moved to heap: a
foo.go:5:9: func literal escapes to heap
```

我们可以看到 `a` 变量是 captured by reference，并且逃逸到堆上。返回的 closure 也在堆上分配空间，但是这里为 closure 分配的内存空间并非是用来放 closure代码的。

要搞清楚 closure 在堆上存了些什么信息，我们可以去看看编译后的汇编代码。

```assembly
"".NewCounter STEXT size=157 args=0x10 locals=0x20 funcid=0x0
	0x0000 00000 (foo.go:3)	TEXT	"".NewCounter(SB), ABIInternal, $32-16
	0x0000 00000 (foo.go:3)	MOVQ	(TLS), CX
	0x0009 00009 (foo.go:3)	CMPQ	SP, 16(CX)
	0x000d 00013 (foo.go:3)	PCDATA	$0, $-2
	0x000d 00013 (foo.go:3)	JLS	147
	0x0013 00019 (foo.go:3)	PCDATA	$0, $-1
	0x0013 00019 (foo.go:3)	SUBQ	$32, SP
	0x0017 00023 (foo.go:3)	MOVQ	BP, 24(SP)
	0x001c 00028 (foo.go:3)	LEAQ	24(SP), BP
	0x0021 00033 (foo.go:3)	FUNCDATA	$0, gclocals·2589ca35330fc0fce83503f4569854a0(SB)
	0x0021 00033 (foo.go:3)	FUNCDATA	$1, gclocals·9fb7f0986f647f17cb53dda1484e0f7a(SB)
	0x0021 00033 (foo.go:4)	LEAQ	type.int(SB), AX ; AX = sizeof(int)
	0x0028 00040 (foo.go:4)	MOVQ	AX, (SP)
	0x002c 00044 (foo.go:4)	PCDATA	$1, $0
	0x002c 00044 (foo.go:4)	CALL	runtime.newobject(SB) ; 为 a 在堆上分配空间
	0x0031 00049 (foo.go:4)	MOVQ	8(SP), AX             ; AX = &a
	0x0036 00054 (foo.go:4)	MOVQ	AX, "".&a+16(SP)      
	0x003b 00059 (foo.go:4)	MOVQ	"".init+40(SP), CX
	0x0040 00064 (foo.go:4)	MOVQ	CX, (AX)              ; *a = init
	0x0043 00067 (foo.go:5)	LEAQ	type.noalg.struct { F uintptr; "".a *int }(SB), CX ; CX = sizeof(struct{F unintptr; a *int})
	0x004a 00074 (foo.go:5)	MOVQ	CX, (SP)
	0x004e 00078 (foo.go:5)	PCDATA	$1, $1
	0x004e 00078 (foo.go:5)	CALL	runtime.newobject(SB) ; 为 closure 分配内存空间
	0x0053 00083 (foo.go:5)	MOVQ	8(SP), AX             ; AX = &closure
	0x0058 00088 (foo.go:5)	LEAQ	"".NewCounter.func1(SB), CX ; CX = 指向 closure 代码的指针
	0x005f 00095 (foo.go:5)	MOVQ	CX, (AX)                    ; closure.F = CX
	0x0062 00098 (foo.go:5)	PCDATA	$0, $-2
	0x0062 00098 (foo.go:5)	CMPL	runtime.writeBarrier(SB), $0
	0x0069 00105 (foo.go:5)	JNE	131
	0x006b 00107 (foo.go:5)	MOVQ	"".&a+16(SP), CX ; CX = &a
	0x0070 00112 (foo.go:5)	MOVQ	CX, 8(AX)        ; closure.a = &a
	0x0074 00116 (foo.go:5)	PCDATA	$0, $-1
	0x0074 00116 (foo.go:5)	MOVQ	AX, "".~r1+48(SP)
	0x0079 00121 (foo.go:5)	MOVQ	24(SP), BP
	0x007e 00126 (foo.go:5)	ADDQ	$32, SP
	0x0082 00130 (foo.go:5)	RET
	0x0083 00131 (foo.go:5)	PCDATA	$0, $-2
	0x0083 00131 (foo.go:5)	LEAQ	8(AX), DI
	0x0087 00135 (foo.go:5)	MOVQ	"".&a+16(SP), CX
	0x008c 00140 (foo.go:5)	CALL	runtime.gcWriteBarrierCX(SB)
	0x0091 00145 (foo.go:5)	JMP	116
	0x0093 00147 (foo.go:5)	NOP
	0x0093 00147 (foo.go:3)	PCDATA	$1, $-1
	0x0093 00147 (foo.go:3)	PCDATA	$0, $-2
	0x0093 00147 (foo.go:3)	CALL	runtime.morestack_noctxt(SB)
	0x0098 00152 (foo.go:3)	PCDATA	$0, $-1
	0x0098 00152 (foo.go:3)	JMP	0

; NewCounter 中返回的 closure 的代码
"".NewCounter.func1 STEXT nosplit size=19 args=0x8 locals=0x0 funcid=0x0
	0x0000 00000 (foo.go:5)	TEXT	"".NewCounter.func1(SB), NOSPLIT|NEEDCTXT|ABIInternal, $0-8
	0x0000 00000 (foo.go:5)	FUNCDATA	$0, gclocals·33cdeccccebe80329f1fdbee7f5874cb(SB)
	0x0000 00000 (foo.go:5)	FUNCDATA	$1, gclocals·33cdeccccebe80329f1fdbee7f5874cb(SB)
	0x0000 00000 (foo.go:5)	MOVQ	8(DX), AX  ; *DX+8 这里存储的是 a 的指针
 	0x0004 00004 (foo.go:6)	MOVQ	(AX), CX   ; CX = &a
	0x0007 00007 (foo.go:6)	INCQ	CX         ; CX++
	0x000a 00010 (foo.go:6)	MOVQ	CX, (AX)   ; *a = CX
	0x000d 00013 (foo.go:7)	MOVQ	CX, "".~r0+8(SP)
	0x0012 00018 (foo.go:7)	RET

```

从上面的汇编中，我们可以看到编译器为 `NewCounter` 内的 closure 生成了一个 `struct {F uintptr; a *int}` 来表示 closure 对象。其中 `F` 是指向实际函数代码的指针，即汇编代码中 `NewCounter.func1`；`a` 是变量 `a` 逃逸到堆上对应的指针。`NewCounter` 就返回了一个 closure 对象的指针。

`NewCounter.func1` 的汇编中，通过 DX 寄存器获取到 `a`，再对 `a` 做操作。这里 `a` 的指针是存储在 `*DX+8` 的位置，我们由此可以推测 DX 存储的就是 closure 对象的指针。

我们可以通过调用 closure 的汇编代码来确认我们的猜测：

```go
package closures

func Bar() {
    count := NewCounter(0)
    _ = count()
}
```

```assembly
"".Bar STEXT size=71 args=0x0 locals=0x18 funcid=0x0
	0x0000 00000 (bar.go:3)	TEXT	"".Bar(SB), ABIInternal, $24-0
	0x0000 00000 (bar.go:3)	MOVQ	(TLS), CX
	0x0009 00009 (bar.go:3)	CMPQ	SP, 16(CX)
	0x000d 00013 (bar.go:3)	PCDATA	$0, $-2
	0x000d 00013 (bar.go:3)	JLS	64
	0x000f 00015 (bar.go:3)	PCDATA	$0, $-1
	0x000f 00015 (bar.go:3)	SUBQ	$24, SP
	0x0013 00019 (bar.go:3)	MOVQ	BP, 16(SP)
	0x0018 00024 (bar.go:3)	LEAQ	16(SP), BP
	0x001d 00029 (bar.go:3)	FUNCDATA	$0, gclocals·33cdeccccebe80329f1fdbee7f5874cb(SB)
	0x001d 00029 (bar.go:3)	FUNCDATA	$1, gclocals·33cdeccccebe80329f1fdbee7f5874cb(SB)
	0x001d 00029 (bar.go:4)	MOVQ	$0, (SP)
	0x0025 00037 (bar.go:4)	PCDATA	$1, $0
	0x0025 00037 (bar.go:4)	CALL	"".NewCounter(SB)
	0x002a 00042 (bar.go:4)	MOVQ	8(SP), DX ; DX = closure 对象的指针
	0x002f 00047 (bar.go:5)	MOVQ	(DX), AX  ; AX = clousre.F （代码指针）
	0x0032 00050 (bar.go:5)	CALL	AX        ; 调用 closure
	0x0034 00052 (bar.go:6)	MOVQ	16(SP), BP
	0x0039 00057 (bar.go:6)	ADDQ	$24, SP
	0x003d 00061 (bar.go:6)	RET
	0x003e 00062 (bar.go:6)	NOP
	0x003e 00062 (bar.go:3)	PCDATA	$1, $-1
	0x003e 00062 (bar.go:3)	PCDATA	$0, $-2
	0x003e 00062 (bar.go:3)	NOP
	0x0040 00064 (bar.go:3)	CALL	runtime.morestack_noctxt(SB)
	0x0045 00069 (bar.go:3)	PCDATA	$0, $-1
	0x0045 00069 (bar.go:3)	JMP	0
```

从调用 closure 的汇编我们可以看到， `NewCounter` 返回了 closure 对象的指针，在调用 closure 前这个指针赋值给 DX 寄存器。这样在 closure 的汇编代码中，我们就能通过 DX 寄存器正确地访问到 closed variable。

至此，我们可以大致总结 closure 在汇编层面的实现如下：

1. 编译器为 closure 生成特别的结构（`struct {F intptr; closed variables...}`）来保存函数指针和 closed variable；
2. closure 函数的汇编中 DX 寄存器的值是这个 closure 对象的指针，通过 DX 可以访问到这个 closure 的 closed variable；
3. 调用 closure 前需要先设置 DX 寄存器的值为 closure 对象的指针。

那么调用函数的地方如何区分这个函数是普通的函数还是一个 closure？对于一部分函数调用，我们可以静态地分析出来被调用的具体的函数，由此可以直接确定调用的方式。其他部分都按照 closure 调用处理，把“函数指针”（对普通函数来说这是一个函数指针，对于 closure 来说这是 closure 对象）赋值给 DX 寄存器——如果被调用的函数是个普通函数，它直接忽略这个 DX 寄存器即可；closure 则能通过 DX 访问 closed variable。读者可以自行用下面的代码验证一下：

```go
func Call(v int, fn func(i int)) {
	fn(v + 5)
}
```

另外这里 closed variable 并非全是指针，也有一部分是非指针类型。是否是指针是由 captured by value 或者 captured by reference 决定的。例如下面的代码 closure 对象的类型就是 `struct { F uintptr; i int }`，因为这个 closure 中变量以 reference 的方式被捕获了（满足上面的 captured by value 的条件）。

```go
package closures

func ByValue1() func() int {
    var i int = 1
    return func() int {
        return i
    }
}
```

---

相比于普通的函数，closure 多了一些动态的、可变的东西，它使得比较静态的函数变得更加像普通的数据，可以被动态地创建出来，可以用于参数的传递。当然更加灵活的同时也带来了更复杂的编译器实现和堆上内存分配的抽象代价。

