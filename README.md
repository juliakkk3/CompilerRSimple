# RSimple Compiler

A complete compiler for the **RSimple** programming language that translates source code into executable .NET programs (CIL/IL code).

## 📋 Table of Contents

- [What is RSimple?](#what-is-rsimple)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Language Grammar](#language-grammar)
- [Lab 5 vs Lab 6](#lab-5-vs-lab-6)
- [Compilation Pipeline](#compilation-pipeline)
- [File Descriptions](#file-descriptions)
- [Code Examples](#code-examples)
- [Quick Start Guide](#quick-start-guide)

---

## 🎯 What is RSimple?

**RSimple** is a simple programming language inspired by R syntax, designed for educational purposes. The compiler translates RSimple code into CIL (Common Intermediate Language) - the intermediate language used by .NET runtime.

### Features:
- **R-style assignment**: `x <- 5` or standard `x = 5`
- **Arithmetic operations**: `+`, `-`, `*`, `/`, `^` (power)
- **Comparison operators**: `<`, `<=`, `>`, `>=`, `==`, `!=`
- **Control flow**: `if-else` statements, `while` loops
- **Input/Output**: `scan()` for input, `print()` for output
- **Boolean constants**: `TRUE`, `FALSE`
- **Comments**: `# This is a comment`

---

## 📁 Project Structure

```
CompilerRSimple/
├── Lab5/                           # Lab 5: Hand-written compiler
│   ├── lexer.py                   # Manual lexical analyzer (FSM)
│   ├── parser.py                  # Manual parser (Recursive Descent)
│   └── main.py                    # Main entry point for Lab 5
├── Lab6/                          # Lab 6: ANTLR4-based compiler
│   ├── RSimple.g4                 # ANTLR4 grammar definition
│   ├── RSimpleLexer.py           # Generated lexer
│   ├── RSimpleParser.py          # Generated parser
│   ├── RSimpleVisitor.py         # Generated visitor base class
│   ├── compiler_visitor.py       # Manual visitor implementation
│   └── main_antlr.py             # Main entry point for Lab 6
├── cil_generator.py              # CIL code generator
├── postfix_translator.py         # Postfix utilities & VM
├── test1.my_lang                 # Example source code
└── README.md                     # This file
```

---

## 🔧 Installation

### Prerequisites

1. **Python 3.8+**
2. **ANTLR4 runtime** (for Lab 6 only):
   ```bash
   pip install antlr4-python3-runtime
   ```
3. **.NET Framework** (for creating .exe files):
   - Windows: Already included
   - Linux/Mac: Install Mono framework

### Optional Tools

- **ilasm.exe**: .NET IL Assembler (usually at `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\ilasm.exe`)

---

## 🚀 Quick Start

### Using Lab 5 (Manual Compiler)

1. **Create your RSimple program** in a `.my_lang` file:
   ```rsimple
   # test1.my_lang
   x <- 5
   y <- 10
   print(x + y)
   ```

2. **Compile and run**:
   ```bash
   python Lab5/main.py test1.my_lang
   ```

3. **Output files**:
   - `test1.il` - CIL assembly code
   - `test1.exe` - Executable (if ilasm found)
   - `test1.postfix` - Intermediate postfix code

4. **Run the executable**:
   ```bash
   ./test1.exe
   # Output: 15.0
   ```

### Using Lab 6 (ANTLR4 Compiler)

1. **Generate ANTLR4 files** (if not already generated):
   ```bash
   cd Lab6
   antlr4 -Dlanguage=Python3 -visitor RSimple.g4
   ```

2. **Create your RSimple program** (same as above)

3. **Compile and run**:
   ```bash
   python Lab6/main_antlr.py test1.my_lang
   ```

4. **Output files**:
   - `test_antlr.il` - CIL assembly code
   - `test_antlr.exe` - Executable

---

## 📖 Language Grammar

### Basic Syntax

#### Variables and Assignment
```rsimple
# R-style assignment
x <- 42

# Standard assignment
y = 3.14

# Variable names: letters, digits, underscore, dot
my_var <- 100
value.sum <- 50
```

#### Arithmetic Operations
```rsimple
# Basic operations
result <- 5 + 3 * 2    # = 11 (multiplication first)
power <- 2 ^ 3         # = 8
negative <- -5

# Right-associative power
calc <- 2 ^ 3 ^ 2      # = 2^(3^2) = 512
```

#### Input and Output
```rsimple
# Input from keyboard
x <- scan()

# Output to console
print(x)
print(x, y, x + y)     # Multiple values
```

#### Conditional Statements
```rsimple
# If statement
if (x > 0) {
    print(x)
}

# If-else statement
if (x > 0) {
    print(x)
} else {
    print(-x)
}

# Single statement (no braces)
if (x > 0) print(x)
```

#### Loops
```rsimple
# While loop
i <- 0
while (i < 10) {
    print(i)
    i <- i + 1
}

# Single statement
while (x < 100) x <- x * 2
```

#### Boolean Expressions
```rsimple
# Boolean constants
flag <- TRUE
done <- FALSE

# Comparisons
result <- x > 5
result <- x == y
result <- x != 0
result <- x >= 10
```

#### Comments
```rsimple
# This is a single-line comment
x <- 5  # Comments can be at end of line
```

### Operator Precedence (highest to lowest)
1. `^` (power) - right-associative
2. `*`, `/` (multiplication, division)
3. `+`, `-` (addition, subtraction)
4. `<`, `<=`, `>`, `>=`, `==`, `!=` (comparison)

---

## 🔄 Lab 5 vs Lab 6

### Lab 5: Hand-Written Compiler

**Approach**: Traditional compiler construction
- **Lexer**: Implemented as Finite State Machine (FSM)
- **Parser**: Recursive Descent Parser
- **Pros**: 
  - Full control over error messages
  - Educational - shows how compilers work internally
  - No external dependencies (except Python)
- **Cons**: 
  - More code to maintain
  - Manual error handling

**Files**:
- `Lab5/lexer.py` - Manual FSM-based lexical analyzer
- `Lab5/parser.py` - Manual recursive descent parser
- `Lab5/main.py` - Compilation driver

### Lab 6: ANTLR4-Based Compiler

**Approach**: Modern compiler generator
- **Lexer & Parser**: Auto-generated from grammar
- **Visitor**: Manual implementation for code generation
- **Pros**: 
  - Less code to write
  - Grammar is declarative and clear
  - Industry-standard tool
- **Cons**: 
  - Requires ANTLR4 runtime
  - Less control over parsing details

**Files**:
- `Lab6/RSimple.g4` - Grammar specification (manual)
- `Lab6/RSimpleLexer.py` - Auto-generated lexer
- `Lab6/RSimpleParser.py` - Auto-generated parser
- `Lab6/RSimpleVisitor.py` - Auto-generated visitor base
- `Lab6/compiler_visitor.py` - Manual visitor implementation
- `Lab6/main_antlr.py` - Compilation driver

### Key Difference

**Lab 5** demonstrates how to build a compiler from scratch, while **Lab 6** shows how to use modern tools (ANTLR4) to achieve the same result with less code.

**Both labs produce identical output** - valid CIL code that can be executed on .NET runtime.

---

## 🔄 Compilation Pipeline

The compiler works in 4 stages:

```
Source Code (.my_lang)
        ↓
    [STAGE 1: LEXICAL ANALYSIS]
        ↓
    Tokens (lexemes)
        ↓
    [STAGE 2: SYNTAX ANALYSIS]
        ↓
    Abstract Syntax Tree (AST)
        ↓
    [STAGE 3: POSTFIX CODE GENERATION]
        ↓
    Postfix Code (intermediate representation)
        ↓
    [STAGE 4: CIL CODE GENERATION]
        ↓
    CIL Assembly (.il)
        ↓
    [ilasm.exe]
        ↓
    Executable (.exe)
```

### Stage 1: Lexical Analysis
**Purpose**: Break source code into tokens (lexemes)

**Input**: Text file with RSimple code
```rsimple
x <- 5 + 3
```

**Output**: Sequence of tokens
```
[(x, id), (<-, assign_op), (5, intnum), (+, add_op), (3, intnum)]
```

**Lab 5**: `lexer.py` uses Finite State Machine
**Lab 6**: `RSimpleLexer.py` generated from grammar

### Stage 2: Syntax Analysis
**Purpose**: Verify syntax correctness and build parse tree

**Input**: Tokens from lexer
**Output**: 
- Parse tree / AST
- Variable table
- Semantic checks (type checking, initialization)

**Lab 5**: `parser.py` implements Recursive Descent
**Lab 6**: `RSimpleParser.py` generates parse tree, `compiler_visitor.py` traverses it

### Stage 3: Postfix Code Generation
**Purpose**: Convert to postfix notation (easier for code generation)

**Why Postfix?**
- Stack-based evaluation (no operator precedence needed)
- Easier to translate to assembly/CIL
- Natural fit for stack machines

**Example**:
```rsimple
x <- 5 + 3 * 2
```

**Postfix**:
```
5
3
2
*
+
=x
```

**Output files**:
- In-memory postfix code list
- `test1.postfix` - Human-readable postfix (optional)

### Stage 4: CIL Code Generation
**Purpose**: Translate postfix code to .NET CIL

**Input**: Postfix code
**Output**: `.il` file with CIL assembly

**Example CIL**:
```cil
.assembly test1 {}
.class Program {
  .method static void Main() {
    .locals init ([0] float32 x)
    ldc.r4 5.0      // push 5
    ldc.r4 3.0      // push 3
    ldc.r4 2.0      // push 2
    mul             // 3 * 2
    add             // 5 + 6
    stloc.0         // store to x
    ret
  }
}
```

**File**: `cil_generator.py` handles this translation

### Stage 5: Assembly (ilasm)
**Purpose**: Convert CIL to executable

**Command**: 
```bash
ilasm test1.il
```

**Output**: `test1.exe` - Runnable .NET program

---

## 📄 File Descriptions

### Core Compiler Files (Manual - Written by Hand)

#### `Lab5/lexer.py`
**Purpose**: Lexical analyzer (tokenizer)
**How it works**:
- Implements Finite State Machine (FSM)
- Reads source code character by character
- Produces tokens: keywords, identifiers, numbers, operators
- Tables: `tokenTable`, `stf` (state transition function), `F` (final states)

**Key components**:
- `Lexer.analyze(source_code)` - main entry point
- `classOfChar()` - determines character class
- `nextState()` - FSM state transitions
- `processing()` - handles token recognition in final states

#### `Lab5/parser.py`
**Purpose**: Syntax analyzer + semantic checker + postfix generator
**How it works**:
- Recursive Descent Parser
- Follows grammar rules
- Generates postfix code during parsing
- Type checking and variable tracking

**Key methods**:
- `Parser.parse()` - main entry point
- `parseStatement()`, `parseExpression()`, etc. - grammar rules
- `addToPostfix()` - adds instruction to postfix code
- `tableOfVar` - tracks variables and their types

#### `Lab5/main.py`
**Purpose**: Main driver for Lab 5 compiler
**What it does**:
1. Reads source file
2. Runs lexer
3. Runs parser
4. Generates CIL code
5. Optionally runs ilasm
6. Optionally executes postfix code (for testing)

**Usage**:
```bash
python Lab5/main.py input.my_lang [output.il]
```

### ANTLR4 Files (Lab 6)

#### `Lab6/RSimple.g4`
**Purpose**: Grammar definition for ANTLR4
**Written by**: Human (manual)
**Content**:
- Parser rules (lowercase): `program`, `statement`, `expression`, etc.
- Lexer rules (uppercase): `IF`, `WHILE`, `ID`, `INT`, etc.

**Generate parser from it**:
```bash
antlr4 -Dlanguage=Python3 -visitor RSimple.g4
```

#### `Lab6/RSimpleLexer.py`
**Purpose**: Lexical analyzer
**Generated by**: ANTLR4 from `RSimple.g4`
**Contains**: Token definitions, lexer state machine (serialized ATN)

#### `Lab6/RSimpleParser.py`
**Purpose**: Syntax analyzer
**Generated by**: ANTLR4 from `RSimple.g4`
**Contains**: Parser rules, parse tree construction

#### `Lab6/RSimpleVisitor.py`
**Purpose**: Base class for tree traversal
**Generated by**: ANTLR4 with `-visitor` flag
**Contains**: `visit*()` methods for each grammar rule

#### `Lab6/compiler_visitor.py`
**Purpose**: Custom visitor that generates postfix code
**Written by**: Human (manual)
**How it works**:
- Extends `RSimpleVisitor`
- Overrides `visit*()` methods
- Generates postfix code while traversing AST
- Maintains variable table

**Key methods**:
- `visitAssignment()` - handles `x <- 5`
- `visitIfStatement()` - handles `if-else`
- `visitArithmExpression()` - handles `+`, `-`
- `visitPower()` - handles `^` (right-associative!)

#### `Lab6/main_antlr.py`
**Purpose**: Main driver for Lab 6 compiler
**What it does**:
1. Reads source file
2. Creates ANTLR4 input stream
3. Runs generated lexer
4. Runs generated parser → builds parse tree
5. Runs custom visitor → generates postfix
6. Generates CIL code
7. Optionally runs ilasm

**Usage**:
```bash
python Lab6/main_antlr.py input.my_lang
```

### Common Compiler Files

#### `cil_generator.py`
**Purpose**: Translates postfix code to CIL assembly
**Written by**: Human (manual)
**How it works**:
- Reads postfix instruction by instruction
- Generates equivalent CIL instructions
- Handles .NET metadata (assembly, class, method)
- Manages local variables

**Key class**: `CILGenerator`
**Methods**:
- `generate()` - main generation
- `_generate_header()` - .NET assembly metadata
- `_generate_instructions()` - postfix → CIL translation
- `_generate_locals()` - local variable declarations

**CIL instruction mapping**:
- Numbers → `ldc.i4`, `ldc.r4` (load constant)
- Variables → `ldloc`, `stloc` (load/store local)
- `+` → `add`
- `-` → `sub`
- `*` → `mul`
- `/` → `div`
- `^` → `call System.Math::Pow`
- `print` → `call System.Console::WriteLine`
- `scan` → `call System.Console::ReadLine`
- `JF` → `brfalse` (branch if false)
- `JMP` → `br` (branch unconditionally)

#### `postfix_translator.py`
**Purpose**: Postfix code utilities
**Written by**: Human (manual)

**Contains**:

1. **`save_postfix_to_file()`**
   - Saves postfix code in PSM format (human-readable)
   - Sections: `.vars`, `.labels`, `.code`
   
2. **`PostfixMachine`** class
   - Virtual machine for executing postfix code
   - Stack-based execution
   - Used for testing/demonstration (NOT part of compilation)
   - Shows what the program will do without running .exe

3. **`print_postfix_code()`**
   - Displays postfix code on screen

**Why PostfixMachine?**
- Educational: shows intermediate representation
- Testing: verify correctness before CIL generation
- Debugging: easier to understand than CIL

### Generated Output Files

#### `*.il` files
**What**: CIL assembly code (text format)
**Generated by**: `cil_generator.py`
**Content**: 
- Assembly metadata
- Class definition
- Main method with CIL instructions
- Local variable declarations

**Example**:
```cil
.assembly test1 {}
.module test1.exe

.class private auto ansi beforefieldinit Program
  extends [mscorlib]System.Object
{
  .method private hidebysig static void Main(string[] args) cil managed
  {
    .entrypoint
    .maxstack 8
    .locals init (
      [0] float32 x
    )
    
    ldc.r4 5.0
    stloc.0
    ret
  }
}
```

#### `*.exe` files
**What**: Executable .NET programs
**Generated by**: `ilasm.exe` (Microsoft IL Assembler)
**Content**: Binary .NET assembly
**Run**: `./test1.exe` or double-click on Windows

#### `*.postfix` files
**What**: Human-readable postfix code (optional)
**Generated by**: `save_postfix_to_file()`
**Format**: PSM (Postfix Stack Machine) v0.3
**Purpose**: Debugging, educational

### Other Files

#### `*.my_lang` files
**What**: Source code files
**Written by**: User (you!)
**Extension**: `.my_lang` (can be anything)
**Contains**: RSimple program code

#### `.gitignore`
**What**: Git configuration
**Purpose**: Excludes generated files from version control
**Typical entries**: `*.exe`, `*.il`, `*.postfix`, `__pycache__/`

---

## 💡 Code Examples

### Example 1: Hello World (Output)

**File**: `hello.my_lang`
```rsimple
# Simple output example
print(42)
print(3.14)
print(TRUE)
```

**Compile**:
```bash
python Lab5/main.py hello.my_lang
```

**Run**:
```bash
./hello.exe
```

**Output**:
```
42.0
3.14
True
```

### Example 2: Calculator with Input

**File**: `calculator.my_lang`
```rsimple
# Simple calculator
x <- scan()
y <- scan()

sum <- x + y
diff <- x - y
prod <- x * y
quot <- x / y

print(sum, diff, prod, quot)
```

**Compile & Run**:
```bash
python Lab5/main.py calculator.my_lang
./calculator.exe
```

**Interaction**:
```
> 10
> 5
15.0
5.0
50.0
2.0
```

### Example 3: Factorial Calculator

**File**: `factorial.my_lang`
```rsimple
# Calculate factorial
n <- scan()
fact <- 1
i <- 1

while (i <= n) {
    fact <- fact * i
    i <- i + 1
}

print(fact)
```

**Test**:
```bash
python Lab5/main.py factorial.my_lang
./factorial.exe
> 5
120.0
```

### Example 4: Conditional Logic

**File**: `absolute.my_lang`
```rsimple
# Absolute value calculator
x <- scan()

if (x < 0) {
    result <- -x
} else {
    result <- x
}

print(result)
```

### Example 5: Power Calculation

**File**: `power.my_lang`
```rsimple
# Power calculations
base <- 2
exp <- 3

# Right-associative: 2^3^2 = 2^(3^2) = 512
result <- base ^ exp ^ 2
print(result)

# With parentheses: (2^3)^2 = 64
result2 <- (base ^ exp) ^ 2
print(result2)
```

**Output**:
```
512.0
64.0
```

---

## 🏗️ Compilation Algorithm (Detailed)

### Step-by-Step Process

#### 1. Source Code Preparation
**Action**: Write RSimple code in `.my_lang` file
**Tools**: Any text editor
**Example**:
```rsimple
x <- 5
y <- 10
print(x + y)
```

#### 2. Lexical Analysis (Tokenization)
**Input**: Source code text
**Process**:
- Character-by-character scanning
- Pattern matching (keywords, identifiers, numbers, operators)
- Token generation

**Output**: List of tokens
```python
[
    (1, 'x', 'id', 1),
    (1, '<-', 'assign_op', ''),
    (1, '5', 'intnum', 1),
    (2, 'y', 'id', 2),
    (2, '<-', 'assign_op', ''),
    (2, '10', 'intnum', 2),
    # ...
]
```

**Implementation**:
- Lab 5: `lexer.py` with FSM
- Lab 6: `RSimpleLexer.py` (ANTLR-generated)

#### 3. Syntax Analysis (Parsing)
**Input**: Token stream
**Process**:
- Verify syntax correctness
- Build parse tree / AST
- Semantic checks:
  - Variable declaration before use
  - Type consistency
  - Initialization tracking

**Output**: 
- Parse tree
- Variable table: `{x: (1, 'numeric', True), y: (2, 'numeric', True)}`
- Error messages (if syntax errors found)

**Implementation**:
- Lab 5: `parser.py` with Recursive Descent
- Lab 6: `RSimpleParser.py` + `compiler_visitor.py`

#### 4. Postfix Code Generation
**Input**: Parse tree + semantic info
**Process**: 
- Convert infix expressions to postfix
- Add labels for control flow
- Generate stack-based instructions

**Output**: Postfix code
```python
[
    '5',        # push 5
    '=x',       # assign to x
    '10',       # push 10
    '=y',       # assign to y
    'x',        # push x value
    'y',        # push y value
    '+',        # add
    'print'     # output
]
```

**Why postfix?**
- No operator precedence needed
- Stack-based (perfect for CIL)
- Easier to generate code from

#### 5. CIL Code Generation
**Input**: Postfix code + variable table
**Process**:
- Generate .NET assembly structure
- Translate postfix instructions to CIL
- Handle local variables
- Add labels for jumps

**Output**: `.il` file
```cil
.assembly test1 {}
.class Program {
  .method static void Main() {
    .locals init (
      [0] float32 x,
      [1] float32 y
    )
    
    ldc.r4 5.0
    stloc.0      # x = 5
    ldc.r4 10.0
    stloc.1      # y = 10
    ldloc.0      # load x
    ldloc.1      # load y
    add          # x + y
    box [mscorlib]System.Single
    call void [mscorlib]System.Console::WriteLine(object)
    ret
  }
}
```

**Implementation**: `cil_generator.py`

#### 6. Assembly (ilasm)
**Input**: `.il` file
**Process**: CIL → native executable
**Command**: `ilasm test1.il`
**Output**: `test1.exe` (Windows) or `.exe` (with Mono on Linux/Mac)

**Tool**: Microsoft IL Assembler (ilasm.exe)

#### 7. Execution
**Command**: `./test1.exe` or double-click
**Output**: Program results
```
15.0
```

---

## 🛠️ Advanced Usage

### Command-Line Options

#### Lab 5
```bash
# Basic compilation
python Lab5/main.py source.my_lang

# Specify output file
python Lab5/main.py source.my_lang output.il

# The compiler automatically:
# - Saves postfix code to source.postfix
# - Executes postfix code (shows expected output)
# - Runs ilasm to create .exe
```

#### Lab 6
```bash
# Basic compilation (ANTLR)
python Lab6/main_antlr.py source.my_lang

# Output: test_antlr.il and test_antlr.exe
```

### Manual Steps

If ilasm is not found automatically:
```bash
# 1. Compile to CIL
python Lab5/main.py test.my_lang

# 2. Manually run ilasm
ilasm test.il

# 3. Run executable
./test.exe
```

### Debugging

**View postfix code**:
```bash
cat test1.postfix
```

**View CIL code**:
```bash
cat test1.il
```

**Execute postfix code** (virtual machine):
Edit `main.py` and set `execute_postfix=True`

---

## 📚 Additional Notes

### Why Two Implementations?

- **Lab 5**: Educational - understand compiler internals
- **Lab 6**: Practical - use industry tools (ANTLR4)

Both produce identical results but show different approaches to compiler construction.

### Postfix Code Purpose

Postfix (Reverse Polish Notation) serves as an **intermediate representation**:
- **Input**: High-level syntax tree
- **Output**: Stack-based instructions
- **Advantages**:
  - Operator precedence already resolved
  - Easy to generate CIL/assembly from
  - Simple stack-based evaluation
  - Can be executed directly (PostfixMachine)

### CIL/IL Purpose

CIL (Common Intermediate Language) is:
- **Platform-independent**: Runs on any .NET runtime
- **JIT-compiled**: Converted to native code at runtime
- **Verifiable**: Type-safe and secure
- **Interoperable**: Can call .NET libraries

---

## 🤝 Contributing

This is an educational project. Feel free to:
- Add language features (arrays, functions, etc.)
- Improve error messages
- Add optimization passes
- Extend the grammar

---

## 📖 References

- [ANTLR4 Documentation](https://www.antlr.org/)
- [CIL Instruction Set](https://en.wikipedia.org/wiki/List_of_CIL_instructions)
- [.NET ECMA-335 Standard](https://www.ecma-international.org/publications-and-standards/standards/ecma-335/)

---

## 📝 License

Educational project for learning compiler construction.

---

**Created as part of university compiler design course (Labs 5 & 6)**


## Quick Start Guide

### Lab 5: Hand-Written Compiler

**Standard Compilation Procedure:**

1. Write the code in the file `test1.my_lang`
2. Run `main.py`
3. In the terminal, execute `.\test1.exe`

### Lab 6: ANTLR4-Based Compiler

**Standard Compilation Procedure:**

1. Write the code in the file `test1.my_lang`
2. Run `main_antlr.py`
3. In the terminal, execute `.\test1_antlr.exe`
