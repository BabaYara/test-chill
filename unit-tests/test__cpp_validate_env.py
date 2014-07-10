import ast
import itertools
import pylang.debug
import random
import unittest

import testchill._cpp_validate_env as validate_env
import testchill.cpp_validate

## Support functions ##
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

def _compile_and_run(expr, target_type, bindings):
    t = ast.fix_missing_locations(ast.Expression(expr.compile_expr(target_type)))
    return eval(compile(t, '<string>', 'eval'), bindings)

def _compile_and_invoke(expr, target_type, bindings, args):
    t = ast.fix_missing_locations(ast.Expression(expr.compile_expr(target_type)))
    return (eval(compile(t, '<string>', 'eval'), bindings))(*args)

def _expr_test(tc, expr, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value):
    freevars = expr.getfreevars(fv_bindings)
    value = _compile_and_run(expr, target_type, rt_bindings)
    tc.assertEqual(exp_freevars, freevars)
    tc.assertEqual(exp_value, value)
    tc.assertEqual(target_type, type(value))

def _expr_test_list(tc, expr, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value):
    freevars = expr.getfreevars(fv_bindings)
    value = _compile_and_run(expr, target_type, rt_bindings)
    tc.assertEqual(exp_freevars, freevars)
    tc.assertEqual(exp_value, value)
    tc.assertEqual(list, type(value))

def _expr_test_invoke(tc, expr, fv_bindings, rt_bindings, target_type, exp_freevars, invoke_args, exp_value):
    freevars = expr.getfreevars(fv_bindings)
    value = _compile_and_invoke(expr, target_type, rt_bindings, invoke_args)
    tc.assertEqual(exp_freevars, freevars)
    tc.assertEqual(exp_value, value)
    tc.assertEqual(target_type.exprtype, type(value))

def lambdatype(param_types, etype):
    return validate_env._pylambdatype(param_types, etype)

def arraytype(dims, etype):
    return validate_env._pyarraytype(dims, etype)


## Test case class ##
class Test_CppValidateEnv(unittest.TestCase):
    def setUp(self):
        ### data for the abstract syntax tree ###
        _const_4 = validate_env._ConstantExpr('4')
        _const_3 = validate_env._ConstantExpr('3')
        _const_2 = validate_env._ConstantExpr('2')
        _const_0 = validate_env._ConstantExpr('0')
        _name_x = validate_env._NameExpr('x')
        _name_y = validate_env._NameExpr('y')
        _name_p = validate_env._NameExpr('p')
        _name_pow = validate_env._NameExpr('pow')
        _attr_px = validate_env._AttributeExpr(_name_p, 'x')
        _attr_py = validate_env._AttributeExpr(_name_p, 'y')
        _add_3_2 = validate_env._BinExpr(_const_3, '+', _const_2)
        _add_x_2 = validate_env._BinExpr(_name_x, '+', _const_2)
        _pow_x_2 = validate_env._BinExpr(_name_x, '**', _const_2)
        
        _name_i = validate_env._NameExpr('i')
        _lambda_i = validate_env._LambdaExpr(['i'],_name_i)
        
        _name_j = validate_env._NameExpr('j')
        _const_10 = validate_env._ConstantExpr('10')
        _mul_i_10 = validate_env._BinExpr(_name_i, '*', _const_10)
        _add_mul_i_10_j = validate_env._BinExpr(_mul_i_10, '+', _name_j)
        _lambda_ij = validate_env._LambdaExpr(['i','j'],_add_mul_i_10_j)
        
        self._ConstantExpr_test_data = [
                (('3',), set(), dict(), int, set(), int(3)),
                (('3',), set(), dict(), float, set(), float(3))
            ]
        self._NameExpr_test_data = [
                (('x',), set(), {'x':3}, int, {'x'}, int(3)),
                (('x',), {'x'}, {'x':3}, int, set(), int(3))
            ]
        self._AttributeExpr_test_data = [
                ((validate_env._NameExpr('p'),'x'), set(), {'p':Point(3,0)}, int, {'p'}, int(3)),
                ((validate_env._NameExpr('p'),'x'), {'p'}, {'p':Point(3,0)}, int, set(), int(3))
            ]
        self._BinExpr_test_data = [
                ((_const_3, '+', _const_2), set(), dict(), int, set(), int(5)),
                ((_const_3, '+', _const_2), set(), dict(), float, set(), float(5)),
                ((_name_x, '+', _const_2), set(), {'x':3}, int, {'x'}, int(5)),
                ((_name_x, '+', _const_2), {'x'}, {'x':3}, int, set(), int(5)),
                ((_const_3, '+', _name_x), set(), {'x':2}, int, {'x'}, int(5)),
                ((_const_3, '+', _name_x), {'x'}, {'x':2}, int, set(), int(5)),
                ((_const_3, '-', _const_2), set(), dict(), int, set(), int(1)),
                ((_const_3, '*', _const_2), set(), dict(), int, set(), int(6)),
                ((_const_3, '/', _const_2), set(), dict(), int, set(), int(1)),
                ((_const_3, '**', _const_2), set(), dict(), int, set(), int(9))
            ]
        self._UnaryExpr_test_data = [
                (('-', _const_3), set(), dict(), int, set(), int(-3)),
                (('-', _add_3_2), set(), dict(), int, set(), int(-5)),
                (('-', _add_x_2), set(), {'x':3}, int, {'x'}, int(-5)),
                (('-', _add_x_2), {'x'}, {'x':3}, int, set(), int(-5))
            ]
        self._LambdaExpr_test_data = [
                (([],_const_3), set(), dict(), lambdatype([],int), set(), tuple(), int(3)),
                (([],_name_x), set(), {'x':3}, lambdatype([],int), {'x'}, tuple(), int(3)),
                ((['x'],_pow_x_2), set(), dict(), lambdatype([int],int), set(), (int(4),), int(16))
            ]
        self._InvokeExpr_test_data = [
                ((_name_pow,[_const_3, _const_2]), set(), dict(), int, {'pow'}, int(9)),
            ]
        self._MatrixGenerator_test_data = [
                (([_const_2],_lambda_i), set(), {'_pyitertools': itertools}, arraytype([None],int), set(), [0, 1]),
                (([None],_lambda_i), set(), {'_pyitertools': itertools}, arraytype([_const_2],int), set(), [0, 1]),
                (([_const_2,_const_3],_lambda_ij), set(), {'_pyitertools': itertools}, arraytype([_const_2,_const_3], int), set(), [0, 1, 2, 10, 11, 12]),
                (([_const_2,_const_3],_lambda_ij), set(), {'_pyitertools': itertools}, arraytype([None,None], int), set(), [0, 1, 2, 10, 11, 12]),
                (([_const_2,None],_lambda_ij), set(), {'_pyitertools': itertools}, arraytype([None,_const_3], int), set(), [0, 1, 2, 10, 11, 12]),
                (([None,_const_3],_lambda_ij), set(), {'_pyitertools': itertools}, arraytype([_const_2,None], int), set(), [0, 1, 2, 10, 11, 12]),
                (([None,None],_lambda_ij), set(), {'_pyitertools': itertools}, arraytype([_const_2,_const_3], int), set(), [0, 1, 2, 10, 11, 12]),
                (([_name_x],_lambda_i), set(), {'_pyitertools': itertools, 'x':2}, arraytype([None],int), {'x'}, [0, 1]),
                (([None],_lambda_i), set(), {'_pyitertools': itertools, 'x':2}, arraytype([_name_x],int), set(), [0, 1]),
            ]
        random.seed(0)
        self._RandomExpr_test_data = [
                ((_const_0,_const_4), set(), {'_pyrandom': random}, int, set(), int(random.random()*4)),
                ((_const_0,_name_x), set(), {'_pyrandom': random, 'x':4}, int, {'x'}, int(random.random()*4)),
                ((_name_x,_const_4), set(), {'_pyrandom': random, 'x':0}, int, {'x'}, int(random.random()*4)),
            ]
        random.seed(0)
        ### data for generating ###
        ### data for parsing ###
        self.parse_procedure_test_data = [
                (('procedure void q()',), ('void', 'q', 0)),
                (('procedure int q()',), ('int', 'q', 0)),
                (('procedure float q()',), ('float', 'q', 0)),
                (('procedure unsigned int q()',), ('unsigned int', 'q', 0)),
                (('procedure void q(in int x)',), ('void', 'q', 1)),
                (('procedure void q(in int x, in int y)',), ('void', 'q', 2)),
            ]
        _mm_proc = '''
            procedure void mm(
                in  float* A    = matrix([an,ambn],evendist2),
                in  float* B    = matrix([ambn,bm],evendist2),
                out float* C    = matrix([an,bm],lambda i,j: 0),
                in  int    ambn = random(8,16),
                in  int    an   = random(8,16),
                in  int    bm   = random(8,16))
            '''
        self.parse_parameter_test_data = [
                (('procedure void mm(in int x)',), [(0, 'x', 'int', 'in', False, set())]),
                (('procedure void mm(out int* x = 10)',), [(0, 'x', 'int*', 'out', True, set())]),
                ((_mm_proc,),[
                        (0, 'A', 'float*', 'in', True, set(['an','ambn','evendist2'])),
                        (1, 'B', 'float*', 'in', True, set(['ambn','bm','evendist2'])),
                        (2, 'C', 'float*', 'out', True, set(['an','bm'])),
                        (3, 'ambn', 'int', 'in', True, set([])),
                        (4, 'an', 'int', 'in', True, set([])),
                        (5, 'bm', 'int', 'in', True, set([]))
                    ]),
            ]
    
    def run_expr_test_data(self, ctor, test_data):
        for ctor_args, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value in test_data:
            expr = ctor(*ctor_args)
            _expr_test(self, expr, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value)
    
    def run_expr_test_data_list(self, ctor, test_data):
        for ctor_args, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value in test_data:
            expr = ctor(*ctor_args)
            _expr_test_list(self, expr, fv_bindings, rt_bindings, target_type, exp_freevars, exp_value)
    
    def run_expr_test_data_invoke(self, ctor, test_data):
        for ctor_args, fv_bindings, rt_bindings, target_type, exp_freevars, invoke_args, exp_value in test_data:
            expr = ctor(*ctor_args)
            _expr_test_invoke(self, expr, fv_bindings, rt_bindings, target_type, exp_freevars, invoke_args, exp_value)
    
    def test__ConstantExpr(self):
        self.run_expr_test_data(validate_env._ConstantExpr, self._ConstantExpr_test_data)
    
    def test__NameExpr(self):
        self.run_expr_test_data(validate_env._NameExpr, self._NameExpr_test_data)
    
    def test__AttributeExpr(self):
        self.run_expr_test_data(validate_env._AttributeExpr, self._AttributeExpr_test_data)
    
    def test__UnaryExpr(self):
        self.run_expr_test_data(validate_env._UnaryExpr, self._UnaryExpr_test_data)
    
    def test__LambdaExpr(self):
        self.run_expr_test_data_invoke(validate_env._LambdaExpr, self._LambdaExpr_test_data)
    
    def test__InvokeExpr(self):
        self.run_expr_test_data(validate_env._InvokeExpr, self._InvokeExpr_test_data)
    
    def test__MatrixGenerator(self):
        self.run_expr_test_data_list(validate_env._MatrixGenerator, self._MatrixGenerator_test_data)
    
    def test__RandomExpr(self):
        self.run_expr_test_data(validate_env._RandomExpr, self._RandomExpr_test_data)
    
    def test_parse_procedure(self):
        parse_func = lambda s: list(testchill.cpp_validate._parse_testproc_script(s))[0]
        for args, expected in self.parse_procedure_test_data:
            rtype_exp, name_exp, param_count_exp = expected
            proc = parse_func(*args)
            self.assertEqual(str(proc.rtype), rtype_exp)
            self.assertEqual(proc.name, name_exp)
            self.assertEqual(len(proc.parameters), param_count_exp)
    
    def test_parse_parameter(self):
        #pylang.debug.enable(['pylang.parser.BaseTextParser.parse'])
        parse_func = lambda s: list(testchill.cpp_validate._parse_testproc_script(s))[0]
        for args, expected in self.parse_parameter_test_data:
            proc = parse_func(*args)
            for param_exp in expected:
                index, name_exp, ctype_exp, direction_exp, has_init_exp, freevars_exp = param_exp
                param = proc.parameters[index]
                self.assertEqual(param.name, name_exp)
                self.assertEqual(str(param.cpptype), ctype_exp)
                self.assertEqual(param.direction, direction_exp)
                self.assertEqual(param.init_expr is not None, has_init_exp)
                self.assertEqual(param.getfreevars(), freevars_exp)
        #pylang.debug.enable(['pylang.parser.BaseTextParser.parse'], False)
            
            
