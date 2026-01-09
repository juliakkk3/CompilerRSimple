import sys
import os
from antlr4 import *
from RSimpleLexer import RSimpleLexer
from RSimpleParser import RSimpleParser
from Lab6.compiler_visitor import RSimpleCompilerVisitor
from cil_generator import CILGenerator
from Lab5.main import run_ilasm

def compile_with_antlr(source_file):
    """Компілює RSimple програму використовуючи ANTLR4"""

    print('='*70)
    print('RSIMPLE → CIL COMPILER (ANTLR4 VERSION)')
    print('Лабораторна робота №6')
    print('='*70)
    print(f'\nВхідний файл: {source_file}')

    # Читання вхідного файлу
    input_stream = FileStream(source_file, encoding='utf-8')

    # ========== КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ (ANTLR4) ==========
    print('\n' + '='*70)
    print('КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ (ANTLR4)')
    print('='*70)
    lexer = RSimpleLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()
    print(f'✓ Розпізнано токенів: {len(token_stream.tokens)}')

    # ========== КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ (ANTLR4) ==========
    print('\n' + '='*70)
    print('КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ (ANTLR4)')
    print('='*70)
    parser = RSimpleParser(token_stream)
    tree = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print(f'✗ Знайдено {parser.getNumberOfSyntaxErrors()} синтаксичних помилок')
        return False

    print('✓ Синтаксичне дерево успішно побудовано')

    # ========== КРОК 3: ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ ==========
    print('\n' + '='*70)
    print('КРОК 3: ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ (VISITOR)')
    print('='*70)
    visitor = RSimpleCompilerVisitor()
    visitor.visit(tree)
    print(f'\n✓ Згенеровано {len(visitor.postfix_code)} інструкцій постфікс-коду')

    print('\nПОСТФІКС-КОД:')
    for item in visitor.postfix_code:
        print(f"  {item}")

    # ========== КРОК 4: ГЕНЕРАЦІЯ CIL-КОДУ ==========
    print('\n' + '='*70)
    print('КРОК 4: ГЕНЕРАЦІЯ CIL-КОДУ')
    print('='*70)

    # Визначаємо ім'я збірки з вхідного файлу
    assembly_name = os.path.splitext(os.path.basename(source_file))[0] + '_antlr'
    output_file = f'{assembly_name}.il'

    cil_gen = CILGenerator(
        visitor.postfix_code,
        visitor.variable_table,
        assembly_name
    )
    cil_gen.save_to_file(output_file)

    # ========== КРОК 5: КОМПІЛЯЦІЯ CIL → EXE ==========
    ilasm_success = run_ilasm(output_file)

    # ========== ПІДСУМОК ==========
    print('\n' + '='*70)
    print('✓ КОМПІЛЯЦІЯ ЗАВЕРШЕНА УСПІШНО!')
    print('='*70)
    print(f'\nВхідний файл:  {source_file}')
    print(f'Вихідний файл: {output_file}')

    if ilasm_success:
        exe_file = output_file.replace('.il', '.exe')
        print(f'Виконуваний файл: {exe_file}')
        print(f'\nДля запуску програми:')
        print(f'  {exe_file}')
        print(f'  або: .\\{os.path.basename(exe_file)}')
    else:
        print(f'\nДля створення виконуваного файлу використайте:')
        print(f'  ilasm {output_file}')
        print(f'\nДля запуску:')
        print(f'  {assembly_name}.exe')

    print('='*70)

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Використання: python main_antlr.py <файл.my_lang>')
        print('Приклад: python main_antlr.py test1.my_lang')
        sys.exit(1)

    success = compile_with_antlr(sys.argv[1])
    sys.exit(0 if success else 1)
