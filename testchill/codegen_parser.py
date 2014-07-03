import ast
import collections
import textwrap
import pylib27.parser

from collections import namedtuple as _nt

grammar = textwrap.dedent(r"""
    
    terminals:
        NL         '[\x0a]'
        WS         '[\x09\x0c-\x0d\x20]+'
        Identifier '[a-zA-Z_][a-zA-Z_0-9]*'
        Integer    '\d+'
        Float      '\d+\.\d+'
        _lparen    '\('
        _rparen    '\)'
        _lbrak     '\['
        _rbrak     '\]'
        _comma     '\,'
        _op_eq     '\='
        _op_add    '\+'
        _op_sub    '\-'
        _op_mul    '\*'
        _op_div    '\/'
        _op_pow    '\*\*'
        _op_dot    '\.'
        
        char       'char'
        double     'double'
        float      'float'
        in         'in'
        int        'int'
        long       'long'
        
    ignore: WS, NL
    rules:
        <test-procedure> ::=
            <type-expr>:rt Identifier:name _lparen <param-expr-list-opt>:params _rparen
                                                            => make_procedure(name, rt, params)
        <type-expr> ::=
            <type-expr>:bt _lbrak <expr>:dim _rbrak         => make_array_type(bt, dim)
            <type-expr>:bt _lbrak _rbrak                    => make_array_type(bt, None)
            <type-expr>:bt _op_mul                          => make_pointer_type(bt)
            <prim-type-expr>:t                              => t
        <prim-type-expr> ::=
            char                                            => make_primitive_type('char', 'c')
            double                                          => make_primitive_type('double', 'd')
            float                                           => make_primitive_type('float','f')
            int                                             => make_primitive_type('int', 'i')
            long                                            => make_primitive_type('long', 'l')
        <param-expr-list-opt> ::=
            <param-expr-list>:l                             => l
            eps                                             => []
        <param-expr-list> ::=
            <param-expr-list>:param_list _comma <param-expr>:param
                                                            => param_list + [param]
            <param-expr>:param                              => [param]
        <param-expr> ::=
            in <type-expr>:t Identifier:name _op_eq <expr>:expr
                                                            => make_parameter(name, t, 'in', expr)
            out <type-expr>:t Identifier:name               => make_parameter(name, t, 'out', None)
        
        <expr> ::=
            <add-expr>:e                                    => e
        <add-expr> ::=
            <add-expr>:l _op_add <mul-expr>:r               => make_bin_op('+', l, r)
            <add-expr>:l _op_sub <mul-expr>:r               => make_bin_op('-', l, r)
            <mul-expr>:e                                    => e
        <mul-expr> ::=
            <mul-expr>:l _op_mul <pow-expr>:r               => make_bin_op('*', l, r)
            <mul-expr>:l _op_div <pow-expr>:r               => make_bin_op('\', l, r)
            <pow-expr>:e                                    => e
        <pow-expr> ::=
            <pow-expr>:l _op_pow <un-expr>:r                => make_bin_op('**', l, r)
            <un-expr>:e                                     => e
        <un-expr> ::=
            <un-expr>:fexpr _lparen <expr-list-opt>:expr_list _rparen
                                                            => make_invoke(fexpr, expr_list)
            _lparen <expr>:e _rparen                        => e
            Identifier:name                                 => make_var_ref(name)
            Float:value                                     => make_num_const(value)
            Integer:value                                   => make_num_const(value)
        <expr-list-opt> ::=
            <expr-list>:expr_list                           => expr_list
            eps                                             => []
        <expr-list> ::=
            <expr-list>:expr_list _comma <expr>:e           => expr_list + [e]
            <expr>:e                                        => [e]
    """)

grammar_terminals = textwrap.dedent(r"""
    terminals:
        NL         '[\x0a]'
        WS         '[\x09\x0c-\x0d\x20]+'
        Identifier '[a-zA-Z_][a-zA-Z_0-9]*'
        Integer    '\d+'
        Float      '\d+\.\d+'
        _lparen    '\('
        _rparen    '\)'
        _lbrak     '\['
        _rbrak     '\]'
        _comma     '\,'
        _op_eq     '\='
        _op_add    '\+'
        _op_sub    '\-'
        _op_mul    '\*'
        _op_div    '\/'
        _op_pow    '\*\*'
        _op_dot    '\.'
        
        char       'char'
        double     'double'
        float      'float'
        in         'in'
        int        'int'
        long       'long'
    ignore: NL, WS
    """)

expr_grammar = textwrap.dedent(r"""
    <expr> ::=
        <add-expr>:e                            => e
    <add-expr> ::=
        <add-expr>:l _op_add:op <mul-expr>:r    => make_binop(l, get_ast_op(op), r)
        <add-expr>:l _op_sub:op <mul-expr>:r    => make_binop(l, get_ast_op(op), r)
        <mul-expr>:e                            => e
    """)
