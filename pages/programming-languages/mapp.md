---
title: Mapp
date: 2020-08-31
template: post-code
hide: true
author: τ
---

```lua
block => {
  a => 2020
  b => "hello"
  c => {"world"}
}

assert(block.a == 2020)
assert(block["b"] == "hello")
assert(block.c{} == "world")

assert(this.block == block)
assert(block{} == nil)
```

```lua
block => {
  fn => {|x, y|
    a = 100
    x*a - y/a
  }
}

assert(block.fn.a == nil)
assert(block.fn{x=>2; y=>100} == 199)
```

```lua
{
  **{"age" => 21; "name" => "yangtau"}  # unpack
  
  "handsome" => true if .age <= 24 else false # `.age` refers to `age` in the same block

  "gf-$i" => gf for i, gf in enumerate ["qi", "rui"]
  
}
```

|header|hello|你好|
|--|--|--|
|abc|edff|世界|
|341||243|
